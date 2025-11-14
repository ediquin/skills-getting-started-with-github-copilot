document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      console.log("Fetched activities:", activities); // <-- Add this line

      // Clear loading message
      activitiesList.innerHTML = "";

      // Clear previous options except the placeholder
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - (details.participants?.length || 0);

        // Add a user icon for each participant for visual appeal
        const participantsList = details.participants && details.participants.length > 0
          ? `<ul>${details.participants.map(p => `<li>👤 ${p}</li>`).join("")}</ul>`
          : "<p><em>No participants yet</em></p>";

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Signed Up Participants:</strong>
            ${participantsList}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    try { activity = document.getElementById("activity").value;
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {st response = await fetch(
          method: "POST",codeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        }
      );  method: "POST",
        }
      const result = await response.json();

      if (response.ok) {it response.json();
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();ent = result.message;
      } else {eDiv.className = "success";
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      } messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      messageDiv.classList.remove("hidden");

      // Hide message after 5 secondsdden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);t(() => {
    } catch (error) {assList.add("hidden");
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");gn up. Please try again.";
      console.error("Error signing up:", error);
    } messageDiv.classList.remove("hidden");
  }); console.error("Error signing up:", error);
    }
  // Initialize app
  fetchActivities();
});/ Initialize app
  fetchActivities();
});
