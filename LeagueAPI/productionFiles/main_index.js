// Define all functions here to be used with various event listeners

// Before submitting the input, ensure that the user enters a mininum summoner length of 3.  
function onSubmitSummonerInput(event){
	// If the input is less than 3 characters long, then fire an alert and do not submit the form
	// Also put the element back in focus
    if(document.getElementById('summonerName').value.length < 3){
        alert('Error, this must be longer than 2 characters.  Please provide a longer input');
        document.getElementById('summonerName').value = "";
        event.preventDefault();
		document.getElementById('summonerName').focus();
    }
}






// Define all event listenrs here

// Invoke the event where the user submits the input
document.addEventListener('submit', onSubmitSummonerInput);