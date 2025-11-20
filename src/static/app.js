document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const participantsList = document.getElementById("participants-list");

  // Unregister participant
  async function unregisterParticipant(activityName, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        // Refresh participants list
        await redrawParticipants(activityName);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      console.error("Error unregistering participant:", error);
    }
  }

  // Redraw participants list
  async function redrawParticipants(activityName) {
    if (!activityName) {
      participantsList.innerHTML = "<p>Select an activity to see registered participants.</p>";
      return;
    }

    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      const participants = activities[activityName].participants;

      participantsList.innerHTML = ""; // Clear existing list

      if (participants.length === 0) {
        participantsList.innerHTML = "<p>No participants registered for this activity yet.</p>";
        return;
      }

      const ul = document.createElement("ul");
      participants.forEach(email => {
        const li = document.createElement("li");
        li.textContent = email;

        const deleteIcon = document.createElement("span");
        deleteIcon.className = "delete-icon";
        deleteIcon.textContent = " 🗑️";
        deleteIcon.onclick = () => unregisterParticipant(activityName, email);

        li.appendChild(deleteIcon);
        ul.appendChild(li);
      });
      participantsList.appendChild(ul);
    } catch (error) {
      participantsList.innerHTML = "<p>Failed to load participants.</p>";
      console.error("Error fetching participants:", error);
    }
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listener for activity selection
      activitySelect.addEventListener("change", (event) => {
        redrawParticipants(event.target.value);
      });

      // Initial draw of participants for the first activity
      if (activitySelect.options.length > 1) {
        activitySelect.selectedIndex = 1; // Select the first activity
        redrawParticipants(activitySelect.value);
      }
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        const selectedActivity = document.getElementById("activity").value;
        signupForm.reset();
        // Refresh participants and activities
        await fetchActivities();
        // Re-select the same activity to show updated participants
        if (selectedActivity) {
          document.getElementById("activity").value = selectedActivity;
          await redrawParticipants(selectedActivity);
        }
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
