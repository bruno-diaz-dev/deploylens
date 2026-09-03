let allDeployments = [];
let selectedEnvironment = "all";

let editingDeploymentId = null; 

async function loadDeployments() {
    const response = await fetch("/api/deployments");
    allDeployments = await response.json();

    updateSummary(allDeployments);
    applyFilters();
}

function renderDeployments(deployments) {
    const container = document.querySelector("#deployments");

    container.innerHTML = "";

    for (const deployment of deployments) {
        const createdAt = deployment.created_at
        ? new Date(deployment.created_at).toLocaleString()
        : "Unknown";

        const card = document.createElement("article");

        const statusClass =
            deployment.status === "healthy"
                ? "healthy"
                : "degraded";

        card.classList.add("deployment-card", statusClass);

        card.innerHTML = `
            <h2>${deployment.service}</h2>
            <p>Environment: ${deployment.environment}</p>
            <p>Version: ${deployment.version}</p>
            <p>Status: ${deployment.status}</p>
            <p><strong>Deployed:</strong> ${createdAt}</p>

            <button class="edit-button" data-id="${deployment.id}">Edit</button>

            <button class="delete-button" data-id="${deployment.id}">Delete</button>
        `;

        container.appendChild(card);


        const editButton = card.querySelector(".edit-button");
        const deleteButton = card.querySelector(".delete-button");

        editButton.addEventListener("click", () => {
            editingDeploymentId = deployment.id;

            document.querySelector("#service").value = deployment.service;
            document.querySelector("#environment").value = deployment.environment;
            document.querySelector("#version").value = deployment.version;
            document.querySelector("#status").value = deployment.status;
            
            submitButton.textContent = "Update deployment";
            cancelEditButton.hidden = false;
        });

        deleteButton.addEventListener("click", async () => {
            const deploymentId = deleteButton.dataset.id;

            const response = await fetch(
                `/api/deployments/${deploymentId}`,
                {
                    method: "DELETE"
                }
            );
            if (response.ok) {
                await loadDeployments();
            }
        });
    }
}

function updateSummary(deployments) {
    const total = deployments.length;

    const healthy = deployments.filter(
        deployment => deployment.status === "healthy"
    ).length;

    const degraded = deployments.filter(
        deployment => deployment.status === "degraded"
    ).length;

    const prod = deployments.filter(
        deployment => deployment.environment === "prod"
    ).length;

    document.querySelector("#total-count").textContent = total;
    document.querySelector("#healthy-count").textContent = healthy;
    document.querySelector("#degraded-count").textContent = degraded;
    document.querySelector("#prod-count").textContent = prod;
}

const filterButtons = document.querySelectorAll("#filters button");
const onlyDegradedCheckbox = document.querySelector("#only-degraded");

function applyFilters() {
    let filteredDeployments = allDeployments;

    if (selectedEnvironment !== "all") {
        filteredDeployments = filteredDeployments.filter(
            deployment => deployment.environment === selectedEnvironment
        );
    }

    if (onlyDegradedCheckbox.checked) {
        filteredDeployments = filteredDeployments.filter(
            deployment => deployment.status === "degraded"
        );
    }

    renderDeployments(filteredDeployments);
}

for (const button of filterButtons) {
    button.addEventListener("click", () => {
        selectedEnvironment = button.dataset.environment;
        applyFilters();
    });
}

onlyDegradedCheckbox.addEventListener("change", () => {
    applyFilters();
});

const deploymentForm =
    document.querySelector("#deployment-form");

const submitButton =
    deploymentForm.querySelector('button[type="submit"]');

const cancelEditButton =
    document.querySelector("#cancel-edit");

deploymentForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const deploymentData = {
        service: document.querySelector("#service").value,
        environment: document.querySelector("#environment").value,
        version: document.querySelector("#version").value,
        status: document.querySelector("#status").value
    };

    let url = "/api/deployments";
    let method = "POST";

    if (editingDeploymentId !== null) {
        url = `/api/deployments/${editingDeploymentId}`;
        method = "PUT";
    }

    const response = await fetch(url, {
        method: method,
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(deploymentData)
    });

    if (response.ok) {
        deploymentForm.reset();
        editingDeploymentId = null;
        
        submitButton.textContent = "Register deployment";
        cancelEditButton.hidden = true;

        await loadDeployments();
    }
});

cancelEditButton.addEventListener("click", () => {
    editingDeploymentId = null;

    deploymentForm.reset();

    submitButton.textContent = "Register deployment";
    cancelEditButton.hidden = true;
});

loadDeployments();