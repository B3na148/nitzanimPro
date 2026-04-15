//listen for the click on the button
document.getElementById('runScript').addEventListener('click', getSearchHistory);

//history pull script
async function getSearchHistory() {
    let userhistory = await chrome.history.search({
        text: '', 
        maxResults: 100
    });

    //send to server function
  try {
        const response = await fetch('http://localhost:5000/save-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userhistory)
        });

        if (response.ok) {
            console.log("succsess");
        }
    } catch (error) {
        console.error("error", error);
    }
}








