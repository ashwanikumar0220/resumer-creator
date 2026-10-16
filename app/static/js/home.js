"use strict";

document.addEventListener("DOMContentLoaded", function () {

    /* ==========================================
       NAVBAR SCROLL EFFECT
    ========================================== */

    const navbar = document.querySelector(".navbar");

    window.addEventListener("scroll", function () {

        if (window.scrollY > 20) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }

    });


    /* ==========================================
       SMOOTH SCROLL
    ========================================== */

    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(function (link) {

        link.addEventListener("click", function (event) {

            const targetId = this.getAttribute("href");

            if (targetId === "#") {
                return;
            }

            /*
             * Do not interfere with /login#signup
             */
            if (targetId === "#signup") {
                return;
            }

            const target = document.querySelector(targetId);

            if (target) {

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }

        });

    });


    /* ==========================================
       SCROLL REVEAL
    ========================================== */

    const sections = document.querySelectorAll(
        ".statement, .ats-section, .comparison, .process, .features, .quotes, .final"
    );

    if ("IntersectionObserver" in window) {

        const observer = new IntersectionObserver(
            function (entries) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add("show");

                        observer.unobserve(entry.target);

                    }

                });

            },
            {
                threshold: 0.12
            }
        );


        sections.forEach(function (section) {

            section.classList.add("reveal");

            observer.observe(section);

        });

    }


    /* ==========================================
       ATS BAR ANIMATION
    ========================================== */

    const atsProgress = document.querySelector(".ats-progress");

    if (atsProgress && "IntersectionObserver" in window) {

        const atsObserver = new IntersectionObserver(
            function (entries) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        atsProgress.classList.add("animate");

                        atsObserver.unobserve(entry.target);

                    }

                });

            },
            {
                threshold: 0.5
            }
        );

        atsObserver.observe(atsProgress);

    }


    /* ==========================================
       LOGIN BUTTON
       Direct navigation is used as a fallback.
    ========================================== */

    const loginButtons = document.querySelectorAll(".login-button");

    loginButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            window.location.href = "/login";

        });

    });


    /* ==========================================
       SIGNUP BUTTON
    ========================================== */

    const signupButtons = document.querySelectorAll(".signup-button");

    signupButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            window.location.href = "/login#signup";

        });

    });


    /* ==========================================
       CURRENT YEAR
    ========================================== */

    const year = document.querySelector(".current-year");

    if (year) {
        year.textContent = new Date().getFullYear();
    }

});