
function numeric(event)
{       
	// Allow only backspace and delete
	if ( event.keyCode == 46 || event.keyCode == 8 ) {
		// let it happen, don't do anything
	
	// Ensure that it is a number and stop the keypress
	}else if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) {

			// let it happen, don't do anything
	}else{
	    event.preventDefault();
	}
}

function numeric_with_dot(event)
{
	// Allow only backspace and delete
	if ( event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 190) {
		// let it happen, don't do anything
	}
	else {
		// Ensure that it is a number and stop the keypress
		if (event.keyCode < 48 || event.keyCode > 57) {
			event.preventDefault();
		}
	}
}