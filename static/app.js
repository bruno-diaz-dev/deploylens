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

            <div class ="deployment-actions">
                <button
                    class="action-button edit-button"
                    data-id="${deployment.id}"
                >
                    Edit
                </button>

                <button
                    class="action-button delete-button"
                    data-id="${deployment.id}"
                >
                    Delete
                </button>

                <button
                    class="action-button history-button"
                    data-id="${deployment.id}"
                >
                    History
                </button>
            </div>
            <div class="deployment-history" hidden></div>
        `;

        container.appendChild(card);


        const editButton = card.querySelector(".edit-button");
        const deleteButton = card.querySelector(".delete-button");
        const historyButton = card.querySelector(".history-button");
        const historyContainer = card.querySelector(".deployment-history");

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

        historyButton.addEventListener("click", async () => {
            if (!historyContainer.hidden) {
                historyContainer.hidden = true;
                historyButton.textContent = "History";
                return;
            }

            const response = await fetch(
                `/api/deployments/${deployment.id}/history`
            );

            if (!response.ok) {
                return;
            }

            const history = await response.json();

            historyContainer.innerHTML = "";

            for (const entry of history) {
                const entryDate = new Date(
                    entry.created_at
                ).toLocaleString();

                const historyItem = document.createElement("div");

                historyItem.classList.add("history-item");

                historyItem.innerHTML = `
                    <div class="history-marker"></div>

                    <div class="history-content">
                        <div class="history-header">
                            <strong>${entry.version}</strong>
                            <span class="history-status ${entry.status}">
                                ${entry.status}
                            </span>
                        </div>

                        <span class="history-environment"
                            ${entry.environment}
                        </span>

                        <small>${entryDate}</small>
                    </div>
                `;

                historyContainer.appendChild(historyItem);
            }

            historyContainer.hidden = false;
            historyButton.textContent = "Hide history";
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

filterButtons[0].classList.add("active");

for (const button of filterButtons) {
    button.addEventListener("click", () => {
        selectedEnvironment = button.dataset.environment;

        for (const filterButton of filterButtons) {
            filterButton.classList.remove("active");
        }

        button.classList.add("active");

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