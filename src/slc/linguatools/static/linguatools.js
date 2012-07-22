jq(document).ready(function(){

	//Hide (Collapse) the toggle containers on load
	jq(".toggle_container").hide();

	//Switch the "Open" and "Close" state per click
	jq(".trigger").toggle(function(){
		jq(this).addClass("active");
		}, function () {
		jq(this).removeClass("active");
	});


	//Slide up and down on click
	jq(".trigger").click(function(){
		jq(this).next(".toggle_container").slideToggle("medium");
        });

});