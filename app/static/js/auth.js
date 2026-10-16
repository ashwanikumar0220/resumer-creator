console.log("Auth JS loaded");

const loginSection = document.getElementById("loginSection");
const signupSection = document.getElementById("signupSection");
const otpSection = document.getElementById("otpSection");

const showSignup = document.getElementById("showSignup");
const showLogin = document.getElementById("showLogin");

const signupForm = document.getElementById("signupForm");
const loginForm = document.getElementById("loginForm");
const otpForm = document.getElementById("otpForm");

let signupEmail = "";


/* SHOW SIGNUP */

showSignup.addEventListener("click", () => {

    loginSection.style.display = "none";
    signupSection.style.display = "block";
    otpSection.style.display = "none";

});


/* SHOW LOGIN */

showLogin.addEventListener("click", () => {

    signupSection.style.display = "none";
    loginSection.style.display = "block";
    otpSection.style.display = "none";

});


/* SIGNUP */

signupForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPassword").value;

    try {

        const response = await fetch("/signup", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })

        });

        const data = await response.json();

        console.log(data);

        if (response.ok) {

            signupEmail = email;

            signupSection.style.display = "none";
            otpSection.style.display = "block";

        } else {

            alert(data.detail || "Signup failed");

        }

    } catch (error) {

        console.error(error);
        alert("Something went wrong");

    }

});


/* VERIFY OTP */

otpForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const otp = document.getElementById("otpInput").value;

    try {

        const response = await fetch("/verify-otp", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: signupEmail,
                otp: otp
            })

        });

        const data = await response.json();

        console.log(data);

        if (response.ok) {

            alert("Email verified successfully!");

            window.location.href = "/editor";

        } else {

            alert(data.detail || "Invalid OTP");

        }

    } catch (error) {

        console.error(error);
        alert("Something went wrong");

    }

});

/* LOGIN */

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Login successful!");
            window.location.href = "/editor";
        } else {
            alert(data.detail || "Login failed");
        }

    } catch (error) {
        console.error(error);
        alert("Something went wrong");
    }
});