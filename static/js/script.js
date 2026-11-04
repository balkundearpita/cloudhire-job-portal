
// CloudHire - Job Search Functionality

function searchJobs() {

    const title = document.getElementById("job-title")
        .value.trim().toLowerCase();

    const location = document.getElementById("job-location")
        .value.trim().toLowerCase();

    const jobCards = document.querySelectorAll(".job-card");

    let matchingJobs = 0;

    jobCards.forEach(function(card) {

        const jobDetails = card.innerText.toLowerCase();

        const titleMatch = jobDetails.includes(title);
        const locationMatch = jobDetails.includes(location);

        if (titleMatch && locationMatch) {

            card.style.display = "block";
            matchingJobs++;

        } else {

            card.style.display = "none";

        }

    });

    const noResults = document.getElementById("no-results");

    if (matchingJobs === 0) {
        noResults.style.display = "block";
    } else {
        noResults.style.display = "none";
    }
}

// Search when Enter key is pressed

document.getElementById("job-title").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        searchJobs();
    }
});

document.getElementById("job-location").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        searchJobs();
    }
});
