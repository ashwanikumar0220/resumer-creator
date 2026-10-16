/* =========================================
   GET ELEMENTS
========================================= */

const homeLink =
    document.getElementById("home-link");

const loginButton =
    document.getElementById("login-button");

const signupButton =
    document.getElementById("signup-button");

const resumeInput =
    document.getElementById("resume-input");

const chooseFileButton =
    document.getElementById("choose-file-button");

const fileName =
    document.getElementById("file-name");

const checkATSButton =
    document.getElementById("check-ats-button");

const loadingSection =
    document.getElementById("loading-section");

const resultSection =
    document.getElementById("result-section");

const atsScore =
    document.getElementById("ats-score");

const skillsScore =
    document.getElementById("skills-score");

const experienceScore =
    document.getElementById("experience-score");

const keywordsScore =
    document.getElementById("keywords-score");

const formattingScore =
    document.getElementById("formatting-score");

const skillsProgress =
    document.getElementById("skills-progress");

const experienceProgress =
    document.getElementById("experience-progress");

const keywordsProgress =
    document.getElementById("keywords-progress");

const formattingProgress =
    document.getElementById("formatting-progress");

const suggestionsList =
    document.getElementById("suggestions-list");


/* =========================================
   HOME
========================================= */

homeLink.addEventListener(
    "click",
    function () {

        window.location.href = "/home";

    }
);


/* =========================================
   LOGIN
========================================= */

loginButton.addEventListener(
    "click",
    function () {

        window.location.href = "/login";

    }
);


/* =========================================
   SIGNUP
========================================= */

signupButton.addEventListener(
    "click",
    function () {

        /*
            Your current application uses
            index.html for authentication.

            Therefore both login and signup
            currently go through /login.
        */

        window.location.href = "/login";

    }
);


/* =========================================
   CHOOSE FILE
========================================= */

chooseFileButton.addEventListener(
    "click",
    function () {

        resumeInput.click();

    }
);


/* =========================================
   FILE SELECTED
========================================= */

resumeInput.addEventListener(
    "change",
    function () {

        const file =
            resumeInput.files[0];


        if (!file) {

            fileName.textContent =
                "No file selected";

            checkATSButton.disabled =
                true;

            return;
        }


        /*
            Make sure it is PDF.
        */

        if (
            file.type !== "application/pdf"
        ) {

            alert(
                "Please select a PDF file."
            );


            resumeInput.value = "";

            fileName.textContent =
                "No file selected";

            checkATSButton.disabled =
                true;

            return;
        }


        fileName.textContent =
            file.name;


        /*
            Now user can click
            Check ATS Score.
        */

        checkATSButton.disabled =
            false;

    }
);


/* =========================================
   CHECK ATS SCORE
========================================= */

checkATSButton.addEventListener(
    "click",
    async function () {

        const file =
            resumeInput.files[0];


        if (!file) {

            alert(
                "Please select a resume first."
            );

            return;
        }


        /*
            Create multipart form data.
        */

        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        /*
            Hide previous result.
        */

        resultSection.classList.add(
            "hidden"
        );


        /*
            Show loading.
        */

        loadingSection.classList.remove(
            "hidden"
        );


        /*
            Prevent multiple clicks.
        */

        checkATSButton.disabled =
            true;


        try {

            const response =
                await fetch(
                    "/ats/analyze",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const result =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    result.detail ||
                    "ATS analysis failed"
                );
            }


            console.log(
                "ATS response:",
                result
            );


            /*
                Put returned data
                into the UI.
            */

            displayATSResult(
                result
            );


        } catch (error) {

            console.error(
                "ATS error:",
                error
            );


            alert(
                error.message ||
                "Something went wrong while analyzing the resume."
            );


        } finally {

            loadingSection.classList.add(
                "hidden"
            );


            checkATSButton.disabled =
                false;
        }

    }
);


/* =========================================
   DISPLAY ATS RESULT
========================================= */

function displayATSResult(result) {

    /*
        Main score.
    */

    atsScore.textContent =
        result.score;


    /*
        Category scores.
    */

    skillsScore.textContent =
        `${result.skills_match}%`;


    experienceScore.textContent =
        `${result.experience}%`;


    keywordsScore.textContent =
        `${result.keywords}%`;


    formattingScore.textContent =
        `${result.formatting}%`;


    /*
        Progress bars.
    */

    skillsProgress.style.width =
        `${result.skills_match}%`;


    experienceProgress.style.width =
        `${result.experience}%`;


    keywordsProgress.style.width =
        `${result.keywords}%`;


    formattingProgress.style.width =
        `${result.formatting}%`;


    /*
        Clear old suggestions.
    */

    suggestionsList.innerHTML = "";


    /*
        Add new suggestions.
    */

    result.suggestions.forEach(
        function (suggestion) {

            const listItem =
                document.createElement("li");


            listItem.textContent =
                suggestion;


            suggestionsList.appendChild(
                listItem
            );

        }
    );


    /*
        Finally show the result.
    */

    resultSection.classList.remove(
        "hidden"
    );


    /*
        Scroll to result.
    */

    resultSection.scrollIntoView({
        behavior: "smooth"
    });
}