$(document).ready(function() {
    // Add click listener to the ChatBot link
    $("#chatbotLink").click(function() {
        $("#layoutSidenav_content").addClass("chat-align"); // Add class on click
    });

    // Add click listener to all navigation links (except ChatBot)
    $(".nav-link").not("#chatbotLink").click(function() {
        $("#layoutSidenav_content").removeClass("chat-align"); // Remove class on click
    });
});