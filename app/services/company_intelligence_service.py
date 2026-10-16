import os
import json
from functools import lru_cache

from groq import Groq


# Curated company profiles. These are general resume-preparation guidelines,
# not official or guaranteed hiring requirements for each company.
COMPANIES = [
    {
        "name": "Google",
        "description": "Technology, search, cloud computing, and AI.",
        "roles": ["Software Engineer", "Data Analyst", "Machine Learning Engineer", "Cloud Engineer", "Site Reliability Engineer", "Product Manager"],
        "skills": ["Data Structures & Algorithms", "Python", "Java", "SQL", "System Design", "Problem Solving"],
        "languages": ["Python", "Java", "C++", "JavaScript", "Go"],
        "tips": ["Demonstrate problem-solving with concrete examples.", "Explain your projects and the decisions you made.", "Use measurable outcomes only when you can support them.", "Keep formatting clear and easy to scan."],
        "career_url": "https://www.google.com/about/careers/",
    },
    {
        "name": "Microsoft",
        "description": "Software, cloud platforms, developer tools, and AI.",
        "roles": ["Software Engineer", "Cloud Engineer", "Data Analyst", "Security Engineer", "Product Manager", "DevOps Engineer"],
        "skills": ["Data Structures & Algorithms", "C#", "Python", "SQL", "Azure", "Problem Solving"],
        "languages": ["C#", "C++", "Python", "Java", "JavaScript", "TypeScript"],
        "tips": ["Highlight software projects and your individual contribution.", "Include relevant cloud or developer-tool experience.", "Explain technical challenges and how you solved them."],
        "career_url": "https://careers.microsoft.com/",
    },
    {
        "name": "Amazon",
        "description": "E-commerce, cloud computing, logistics, and technology.",
        "roles": ["Software Development Engineer", "Cloud Engineer", "Data Engineer", "Business Analyst", "Solutions Architect", "DevOps Engineer"],
        "skills": ["Data Structures & Algorithms", "Java", "Python", "SQL", "AWS", "Problem Solving"],
        "languages": ["Java", "Python", "C++", "JavaScript", "SQL"],
        "tips": ["Describe ownership of specific tasks or projects.", "Explain the impact of your work with evidence.", "Prepare clear examples of technical decisions and trade-offs."],
        "career_url": "https://www.amazon.jobs/",
    },
    {
        "name": "Oracle",
        "description": "Enterprise software, databases, and cloud infrastructure.",
        "roles": ["Software Developer", "Database Engineer", "Cloud Engineer", "Java Developer", "Database Administrator", "Technical Consultant"],
        "skills": ["SQL", "Java", "Python", "Databases", "Cloud Computing", "Problem Solving"],
        "languages": ["Java", "SQL", "Python", "JavaScript", "C++"],
        "tips": ["Highlight database and backend projects when relevant.", "Mention technologies you have actually used.", "Explain how your code or design addressed a problem."],
        "career_url": "https://www.oracle.com/careers/",
    },
    {
        "name": "Meta",
        "description": "Social technology, messaging, infrastructure, and AI.",
        "roles": ["Software Engineer", "Data Engineer", "Machine Learning Engineer", "Product Designer", "Data Scientist"],
        "skills": ["Data Structures & Algorithms", "Python", "C++", "System Design", "SQL"],
        "languages": ["Python", "C++", "Java", "JavaScript", "Hack"],
        "tips": ["Show the engineering work behind your projects.", "Explain performance improvements only when measured.", "Highlight collaboration and technical problem-solving."],
        "career_url": "https://www.metacareers.com/",
    },
    {
        "name": "Apple",
        "description": "Consumer technology, operating systems, devices, and services.",
        "roles": ["Software Engineer", "iOS Developer", "Machine Learning Engineer", "Hardware Engineer", "QA Engineer"],
        "skills": ["Swift", "Python", "C++", "Algorithms", "Software Design", "Testing"],
        "languages": ["Swift", "Objective-C", "Python", "C++", "Java"],
        "tips": ["Show attention to quality and user experience.", "Include relevant apps or software projects.", "Describe your contribution and technical choices clearly."],
        "career_url": "https://www.apple.com/careers/",
    },
    {
        "name": "TCS",
        "description": "IT services, consulting, and enterprise technology.",
        "roles": ["Assistant System Engineer", "Software Developer", "Data Analyst", "Java Developer", "Systems Engineer", "Cloud Engineer"],
        "skills": ["Programming Fundamentals", "Java", "Python", "SQL", "OOP", "Communication"],
        "languages": ["Java", "Python", "C", "C++", "SQL"],
        "tips": ["Show strong programming fundamentals and academic projects.", "List relevant coursework and certifications accurately.", "Keep your skills section aligned with the target role."],
        "career_url": "https://www.tcs.com/careers",
    },
    {
        "name": "Infosys",
        "description": "Digital services, consulting, and enterprise solutions.",
        "roles": ["Systems Engineer", "Software Developer", "Data Analyst", "Cloud Engineer", "Java Developer", "Cybersecurity Analyst"],
        "skills": ["Programming Fundamentals", "Java", "Python", "SQL", "OOP", "Problem Solving"],
        "languages": ["Java", "Python", "C++", "JavaScript", "SQL"],
        "tips": ["Include academic and personal projects relevant to the role.", "Explain your contribution instead of listing only project names.", "Present technical skills honestly and clearly."],
        "career_url": "https://www.infosys.com/careers/",
    },
    {
        "name": "Adobe",
        "description": "Creative software, digital experiences, and AI tools.",
        "roles": ["Software Engineer", "Frontend Developer", "Data Scientist", "Product Designer", "Machine Learning Engineer"],
        "skills": ["JavaScript", "Python", "Algorithms", "React", "SQL", "Problem Solving"],
        "languages": ["JavaScript", "Python", "Java", "C++", "TypeScript"],
        "tips": ["Include projects that demonstrate thoughtful implementation.", "Highlight relevant frontend, data, or software engineering skills.", "Link to working projects or code repositories when available."],
        "career_url": "https://careers.adobe.com/",
    },
    {
        "name": "Accenture",
        "description": "Technology consulting, digital transformation, cloud, and managed services.",
        "roles": ["Application Developer", "Software Engineer", "Data Analyst", "Cloud Engineer", "Cybersecurity Analyst", "Business Analyst"],
        "skills": ["Problem Solving", "SQL", "Python", "Java", "Cloud Fundamentals", "Communication"],
        "languages": ["Python", "Java", "JavaScript", "SQL", "C#"],
        "tips": ["Show how your technical work solves a business problem.", "Highlight teamwork, communication, and client-oriented projects.", "List certifications only when earned."],
        "career_url": "https://www.accenture.com/careers",
    },
    {
        "name": "Deloitte",
        "description": "Professional services, consulting, risk advisory, and technology.",
        "roles": ["Technology Analyst", "Software Engineer", "Business Analyst", "Data Analyst", "Cybersecurity Analyst", "Cloud Consultant"],
        "skills": ["Analytical Thinking", "SQL", "Python", "Excel", "Communication", "Problem Solving"],
        "languages": ["Python", "SQL", "Java", "JavaScript", "C#"],
        "tips": ["Connect your skills to measurable business or user outcomes.", "Present analysis and recommendations clearly.", "Include relevant coursework, case projects, or internships."],
        "career_url": "https://www.deloitte.com/global/en/careers.html",
    },
    {
        "name": "IBM",
        "description": "Enterprise computing, hybrid cloud, AI, and consulting.",
        "roles": ["Software Developer", "Data Scientist", "AI Engineer", "Cloud Engineer", "Cybersecurity Consultant", "Technical Support Engineer"],
        "skills": ["Python", "Java", "SQL", "Cloud Computing", "Machine Learning", "Linux"],
        "languages": ["Python", "Java", "C++", "JavaScript", "SQL"],
        "tips": ["Highlight enterprise, AI, cloud, or open-source projects that match the role.", "Explain your technical decisions and results.", "Show that you can learn unfamiliar tools."],
        "career_url": "https://www.ibm.com/careers",
    },
    {
        "name": "Cisco",
        "description": "Networking, cybersecurity, collaboration, and infrastructure technology.",
        "roles": ["Software Engineer", "Network Engineer", "Security Engineer", "Technical Consulting Engineer", "Site Reliability Engineer"],
        "skills": ["Networking", "Linux", "Python", "TCP/IP", "Cybersecurity", "Troubleshooting"],
        "languages": ["Python", "C", "C++", "Java", "JavaScript"],
        "tips": ["Include networking labs or infrastructure projects where relevant.", "Describe debugging methods and technical outcomes.", "List relevant certifications accurately."],
        "career_url": "https://jobs.cisco.com/",
    },
    {
        "name": "NVIDIA",
        "description": "Accelerated computing, graphics processing, AI, and autonomous systems.",
        "roles": ["Software Engineer", "CUDA Engineer", "AI Engineer", "Machine Learning Engineer", "Hardware Engineer"],
        "skills": ["C++", "Python", "Algorithms", "Parallel Computing", "Linear Algebra", "Machine Learning"],
        "languages": ["C++", "Python", "CUDA C++", "C", "Java"],
        "tips": ["Show relevant systems, graphics, AI, or performance-focused projects.", "Explain benchmarks only when you measured them.", "Highlight mathematical or low-level programming knowledge when relevant."],
        "career_url": "https://www.nvidia.com/en-us/about-nvidia/careers/",
    },
    {
        "name": "Intel",
        "description": "Semiconductors, processors, computing platforms, and hardware software.",
        "roles": ["Software Engineer", "Hardware Engineer", "Firmware Engineer", "Validation Engineer", "AI Software Engineer"],
        "skills": ["C", "C++", "Python", "Computer Architecture", "Linux", "Testing"],
        "languages": ["C", "C++", "Python", "SystemVerilog", "Java"],
        "tips": ["Highlight computer architecture, systems, or hardware-related coursework when relevant.", "Describe testing and debugging methods.", "Distinguish academic projects from professional experience."],
        "career_url": "https://jobs.intel.com/",
    },
    {
        "name": "Qualcomm",
        "description": "Wireless technology, mobile processors, embedded systems, and connectivity.",
        "roles": ["Embedded Software Engineer", "Software Engineer", "Firmware Engineer", "DSP Engineer", "Hardware Engineer"],
        "skills": ["C", "C++", "Embedded Systems", "Operating Systems", "Digital Signal Processing", "Debugging"],
        "languages": ["C", "C++", "Python", "Assembly", "Java"],
        "tips": ["Show embedded, systems, wireless, or hardware-software projects where relevant.", "Explain constraints and debugging techniques.", "Include relevant lab work and technical coursework."],
        "career_url": "https://www.qualcomm.com/company/careers",
    },
    {
        "name": "Samsung",
        "description": "Consumer electronics, mobile devices, semiconductors, and connected products.",
        "roles": ["Software Engineer", "Android Developer", "Embedded Engineer", "QA Engineer", "Data Analyst"],
        "skills": ["Java", "Kotlin", "C++", "Python", "Testing", "Problem Solving"],
        "languages": ["Kotlin", "Java", "C++", "Python", "JavaScript"],
        "tips": ["Show apps, embedded projects, or quality-focused engineering work.", "Mention device or platform experience only if applicable.", "Describe your contribution clearly."],
        "career_url": "https://www.samsung.com/us/careers/",
    },
    {
        "name": "Wipro",
        "description": "IT consulting, engineering services, cloud, and digital transformation.",
        "roles": ["Project Engineer", "Software Developer", "Java Developer", "Data Analyst", "Cloud Engineer", "Test Engineer"],
        "skills": ["Programming Fundamentals", "Java", "Python", "SQL", "Testing", "Communication"],
        "languages": ["Java", "Python", "C", "C++", "SQL"],
        "tips": ["Emphasize fundamentals and practical project work.", "Explain your role in team projects.", "Keep skills and certifications relevant to the position."],
        "career_url": "https://careers.wipro.com/",
    },
    {
        "name": "HCLTech",
        "description": "IT services, engineering, infrastructure, and digital solutions.",
        "roles": ["Software Engineer", "Graduate Engineer Trainee", "Cloud Engineer", "Network Engineer", "Data Analyst"],
        "skills": ["Java", "Python", "SQL", "Linux", "Networking", "Problem Solving"],
        "languages": ["Java", "Python", "C++", "JavaScript", "SQL"],
        "tips": ["Show practical coding and troubleshooting examples.", "Highlight relevant academic or personal projects.", "Be precise about tools and technologies you have used."],
        "career_url": "https://www.hcltech.com/careers",
    },
    {
        "name": "Tech Mahindra",
        "description": "IT services, telecom technology, consulting, and digital engineering.",
        "roles": ["Software Engineer", "Network Engineer", "Java Developer", "Data Analyst", "QA Engineer"],
        "skills": ["Java", "Python", "SQL", "Networking", "Testing", "Communication"],
        "languages": ["Java", "Python", "C++", "JavaScript", "SQL"],
        "tips": ["Connect your technical skills to the role you want.", "Include relevant programming and networking projects.", "Use concise bullet points that explain your contribution."],
        "career_url": "https://www.techmahindra.com/careers/",
    },
    {
        "name": "Capgemini",
        "description": "Technology consulting, engineering, cloud, and digital services.",
        "roles": ["Software Engineer", "Analyst", "Java Developer", "Data Analyst", "Cloud Engineer", "Test Engineer"],
        "skills": ["Java", "Python", "SQL", "Agile", "Cloud Fundamentals", "Problem Solving"],
        "languages": ["Java", "Python", "JavaScript", "C++", "SQL"],
        "tips": ["Show collaboration and structured problem-solving.", "Describe project deliverables and your individual contribution.", "Include relevant tools and certifications accurately."],
        "career_url": "https://www.capgemini.com/careers/",
    },
    {
        "name": "Cognizant",
        "description": "IT consulting, digital engineering, data, and business technology services.",
        "roles": ["Programmer Analyst", "Software Engineer", "Java Developer", "Data Analyst", "QA Engineer", "Cloud Engineer"],
        "skills": ["Java", "Python", "SQL", "OOP", "Testing", "Communication"],
        "languages": ["Java", "Python", "C#", "JavaScript", "SQL"],
        "tips": ["Demonstrate strong fundamentals through projects.", "Explain testing and debugging practices.", "Tailor skills to the actual job description."],
        "career_url": "https://careers.cognizant.com/",
    },
    {
        "name": "LTIMindtree",
        "description": "Digital transformation, IT consulting, data, and cloud services.",
        "roles": ["Graduate Engineer Trainee", "Software Engineer", "Data Engineer", "Java Developer", "Cloud Engineer"],
        "skills": ["Java", "Python", "SQL", "Data Structures", "Cloud Fundamentals", "Problem Solving"],
        "languages": ["Java", "Python", "C++", "JavaScript", "SQL"],
        "tips": ["Highlight academic projects that demonstrate practical skills.", "Explain the technologies used and why.", "Keep the resume readable and role-focused."],
        "career_url": "https://www.ltimindtree.com/careers/",
    },
    {
        "name": "PayPal",
        "description": "Digital payments, financial technology, and online commerce.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Analyst", "Security Engineer", "Site Reliability Engineer"],
        "skills": ["Java", "Python", "SQL", "APIs", "Distributed Systems", "Security"],
        "languages": ["Java", "Python", "JavaScript", "C++", "SQL"],
        "tips": ["Highlight secure, reliable backend or payment-related projects if applicable.", "Describe API design and testing experience.", "Avoid claiming security expertise without supporting examples."],
        "career_url": "https://www.paypal.com/us/webapps/mpp/jobs",
    },
    {
        "name": "Stripe",
        "description": "Financial infrastructure, payment APIs, and online commerce tools.",
        "roles": ["Software Engineer", "Backend Engineer", "Developer Productivity Engineer", "Data Analyst", "Product Designer"],
        "skills": ["APIs", "Backend Development", "SQL", "Distributed Systems", "Testing", "Problem Solving"],
        "languages": ["Ruby", "JavaScript", "TypeScript", "Python", "Java"],
        "tips": ["Show clean API design and developer-focused projects.", "Explain reliability, testing, and edge cases.", "Provide links to useful code samples when available."],
        "career_url": "https://stripe.com/jobs",
    },
    {
        "name": "Uber",
        "description": "Mobility, delivery, logistics, mapping, and marketplace technology.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Scientist", "Data Analyst", "Machine Learning Engineer"],
        "skills": ["Algorithms", "Python", "Java", "SQL", "Distributed Systems", "Experimentation"],
        "languages": ["Python", "Java", "Go", "C++", "JavaScript"],
        "tips": ["Explain how your work handles scale or real-world constraints.", "Show data-driven reasoning when supported by evidence.", "Highlight reliable, tested implementations."],
        "career_url": "https://www.uber.com/us/en/careers/",
    },
    {
        "name": "Airbnb",
        "description": "Travel marketplace, hosting, and hospitality technology.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Scientist", "Data Analyst", "Product Designer"],
        "skills": ["Python", "JavaScript", "SQL", "APIs", "Data Analysis", "User Experience"],
        "languages": ["Python", "JavaScript", "Java", "Kotlin", "SQL"],
        "tips": ["Connect technical decisions to user needs.", "Include product or marketplace projects if relevant.", "Explain your own contribution and the outcome."],
        "career_url": "https://careers.airbnb.com/",
    },
    {
        "name": "Netflix",
        "description": "Streaming entertainment, content technology, and cloud-scale systems.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Engineer", "Machine Learning Engineer", "Security Engineer"],
        "skills": ["Distributed Systems", "Java", "Python", "Cloud Computing", "Data Engineering", "Testing"],
        "languages": ["Java", "Python", "JavaScript", "Kotlin", "Go"],
        "tips": ["Show robust systems or data projects where relevant.", "Describe trade-offs and how you validated decisions.", "Use specific evidence rather than broad claims."],
        "career_url": "https://jobs.netflix.com/",
    },
    {
        "name": "Spotify",
        "description": "Audio streaming, personalization, music technology, and creator tools.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Scientist", "Machine Learning Engineer", "Data Analyst"],
        "skills": ["Python", "Java", "SQL", "Data Analysis", "Machine Learning", "APIs"],
        "languages": ["Python", "Java", "JavaScript", "TypeScript", "SQL"],
        "tips": ["Show projects involving personalization, data, or media when relevant.", "Explain how you evaluated results.", "Include a portfolio or repository for relevant work."],
        "career_url": "https://www.lifeatspotify.com/jobs",
    },
    {
        "name": "Salesforce",
        "description": "Customer relationship management software, cloud applications, and enterprise AI.",
        "roles": ["Software Engineer", "Salesforce Developer", "Business Analyst", "Data Engineer", "Security Engineer"],
        "skills": ["Apex", "JavaScript", "SQL", "Cloud Computing", "APIs", "Problem Solving"],
        "languages": ["Apex", "Java", "JavaScript", "Python", "SQL"],
        "tips": ["Highlight CRM, API, or cloud projects when relevant.", "List platform certifications only if earned.", "Explain how your work improved a workflow or user experience."],
        "career_url": "https://careers.salesforce.com/",
    },
    {
        "name": "ServiceNow",
        "description": "Enterprise workflow automation, IT service management, and cloud software.",
        "roles": ["Software Engineer", "Platform Developer", "Technical Consultant", "Security Engineer", "Data Analyst"],
        "skills": ["JavaScript", "Java", "APIs", "SQL", "Workflow Automation", "Cloud Fundamentals"],
        "languages": ["JavaScript", "Java", "Python", "SQL", "TypeScript"],
        "tips": ["Show workflow automation or full-stack projects.", "Explain how your solution reduced manual work if measured.", "Include platform training or certifications accurately."],
        "career_url": "https://careers.servicenow.com/",
    },
    {
        "name": "Atlassian",
        "description": "Collaboration and developer tools including Jira and Confluence.",
        "roles": ["Software Engineer", "Backend Engineer", "Frontend Developer", "Site Reliability Engineer", "Product Manager"],
        "skills": ["Java", "TypeScript", "React", "APIs", "Cloud Computing", "Testing"],
        "languages": ["Java", "JavaScript", "TypeScript", "Python", "Kotlin"],
        "tips": ["Show tools or workflows that help teams collaborate.", "Highlight maintainable code and testing.", "Link to a working project when possible."],
        "career_url": "https://www.atlassian.com/company/careers",
    },
    {
        "name": "LinkedIn",
        "description": "Professional networking, recruiting technology, and business content.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Scientist", "Machine Learning Engineer", "Product Designer"],
        "skills": ["Java", "Python", "SQL", "Distributed Systems", "Data Analysis", "Algorithms"],
        "languages": ["Java", "Python", "JavaScript", "TypeScript", "Scala"],
        "tips": ["Highlight user-facing or data-intensive projects.", "Explain how you evaluated quality and performance.", "Show collaboration and clear technical communication."],
        "career_url": "https://careers.linkedin.com/",
    },
    {
        "name": "JPMorganChase",
        "description": "Financial services, banking, risk technology, and digital platforms.",
        "roles": ["Software Engineer", "Data Analyst", "Quantitative Analyst", "Cybersecurity Analyst", "Business Analyst"],
        "skills": ["Java", "Python", "SQL", "Data Structures", "Security", "Analytical Thinking"],
        "languages": ["Java", "Python", "C++", "JavaScript", "SQL"],
        "tips": ["Demonstrate accuracy, reliability, and analytical thinking.", "Highlight relevant data, backend, or security projects.", "Describe technical work precisely and honestly."],
        "career_url": "https://careers.jpmorgan.com/",
    },
    {
        "name": "Goldman Sachs",
        "description": "Investment banking, financial markets, asset management, and financial technology.",
        "roles": ["Software Engineer", "Quantitative Analyst", "Data Engineer", "Cybersecurity Analyst", "Business Analyst"],
        "skills": ["Python", "Java", "C++", "SQL", "Statistics", "Problem Solving"],
        "languages": ["Python", "Java", "C++", "JavaScript", "SQL"],
        "tips": ["Show analytical ability and strong technical fundamentals.", "Include relevant statistics, finance, or systems projects.", "Explain assumptions and validation in your work."],
        "career_url": "https://www.goldmansachs.com/careers",
    },
    {
        "name": "Flipkart",
        "description": "E-commerce, supply chain, marketplace, and digital payments technology.",
        "roles": ["Software Development Engineer", "Backend Engineer", "Data Analyst", "Data Scientist", "Product Manager"],
        "skills": ["Data Structures & Algorithms", "Java", "Python", "SQL", "Distributed Systems", "Problem Solving"],
        "languages": ["Java", "Python", "C++", "JavaScript", "Kotlin"],
        "tips": ["Show scalable backend or commerce-related projects where relevant.", "Explain design decisions and edge cases.", "Include measurable outcomes only when verified."],
        "career_url": "https://www.flipkartcareers.com/",
    },
    {
        "name": "PhonePe",
        "description": "Digital payments, financial technology, and consumer financial services.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Analyst", "Data Scientist", "Security Engineer"],
        "skills": ["Java", "Kotlin", "Python", "SQL", "APIs", "Security"],
        "languages": ["Java", "Kotlin", "Python", "JavaScript", "SQL"],
        "tips": ["Highlight reliable backend, API, or data projects.", "Describe testing and failure handling.", "Avoid overstating payment or security experience."],
        "career_url": "https://www.phonepe.com/careers/",
    },
    {
        "name": "Razorpay",
        "description": "Payment infrastructure, business banking, and financial technology.",
        "roles": ["Software Engineer", "Backend Engineer", "Frontend Developer", "Data Analyst", "Security Engineer"],
        "skills": ["Backend Development", "APIs", "SQL", "JavaScript", "Python", "Security"],
        "languages": ["Go", "Java", "Python", "JavaScript", "Ruby"],
        "tips": ["Show API integrations and robust error handling.", "Highlight security and testing practices where applicable.", "Explain the user or business problem your project solves."],
        "career_url": "https://razorpay.com/jobs/",
    },
    {
        "name": "Zomato",
        "description": "Food ordering, restaurant discovery, and delivery technology.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Analyst", "Data Scientist", "Product Manager"],
        "skills": ["Python", "Java", "SQL", "APIs", "Data Analysis", "Problem Solving"],
        "languages": ["Python", "Java", "Go", "JavaScript", "SQL"],
        "tips": ["Highlight marketplace, data, or backend projects.", "Explain how you test reliability and edge cases.", "Tie project results to evidence rather than estimates."],
        "career_url": "https://www.zomato.com/careers",
    },
    {
        "name": "Swiggy",
        "description": "Food delivery, quick commerce, logistics, and marketplace technology.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Analyst", "Machine Learning Engineer", "Product Analyst"],
        "skills": ["Python", "Java", "SQL", "Data Structures", "APIs", "Data Analysis"],
        "languages": ["Java", "Python", "Go", "JavaScript", "SQL"],
        "tips": ["Show projects involving logistics, marketplaces, or data if relevant.", "Explain how your solution handles errors and changing inputs.", "Keep project descriptions specific and verifiable."],
        "career_url": "https://www.swiggy.com/corporate/careers/",
    },
    {
        "name": "Zoho",
        "description": "Business software, SaaS applications, and productivity tools.",
        "roles": ["Software Developer", "Java Developer", "Frontend Developer", "QA Engineer", "Technical Support Engineer"],
        "skills": ["Java", "C++", "JavaScript", "SQL", "Data Structures", "Problem Solving"],
        "languages": ["Java", "C", "C++", "Python", "JavaScript"],
        "tips": ["Demonstrate strong coding fundamentals with working projects.", "Explain your own contribution to each project.", "Include debugging, testing, and practical implementation details."],
        "career_url": "https://www.zoho.com/careers.html",
    },
    {
        "name": "Freshworks",
        "description": "Customer and employee experience software and cloud business applications.",
        "roles": ["Software Engineer", "Frontend Developer", "Backend Engineer", "Data Analyst", "Product Designer"],
        "skills": ["JavaScript", "TypeScript", "React", "Python", "SQL", "APIs"],
        "languages": ["JavaScript", "TypeScript", "Ruby", "Python", "Java"],
        "tips": ["Show user-focused software and clean interface work.", "Highlight testing, accessibility, or maintainability when relevant.", "Provide project links that demonstrate your work."],
        "career_url": "https://www.freshworks.com/company/careers/",
    },
    {
        "name": "BYJU'S",
        "description": "Education technology and digital learning products.",
        "roles": ["Software Engineer", "Frontend Developer", "Backend Developer", "Data Analyst", "Product Analyst"],
        "skills": ["JavaScript", "React", "Python", "SQL", "APIs", "User Experience"],
        "languages": ["JavaScript", "TypeScript", "Python", "Java", "SQL"],
        "tips": ["Show projects that improve learning or user experience.", "Describe your implementation and testing clearly.", "Verify current openings and company details through official sources."],
        "career_url": "https://byjus.com/careers/",
    },
    {
        "name": "Paytm",
        "description": "Digital payments, commerce, financial services, and mobile technology.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Analyst", "Android Developer", "Security Engineer"],
        "skills": ["Java", "Kotlin", "Python", "SQL", "APIs", "Security"],
        "languages": ["Java", "Kotlin", "Python", "JavaScript", "SQL"],
        "tips": ["Highlight mobile, API, or data projects where relevant.", "Explain how you handle failures and validate results.", "Be accurate about security and payment-related experience."],
        "career_url": "https://paytm.com/careers/",
    },
    {
        "name": "Dell Technologies",
        "description": "Computing hardware, enterprise infrastructure, storage, and IT solutions.",
        "roles": ["Software Engineer", "Systems Engineer", "Cloud Engineer", "Cybersecurity Analyst", "Data Analyst"],
        "skills": ["Python", "C++", "Linux", "Networking", "Cloud Computing", "Testing"],
        "languages": ["Python", "C++", "Java", "JavaScript", "SQL"],
        "tips": ["Highlight relevant systems, infrastructure, or application projects.", "Explain your testing and debugging approach.", "Mention hardware or cloud exposure only when applicable."],
        "career_url": "https://jobs.dell.com/",
    },
    {
        "name": "HP",
        "description": "Personal computing, printers, devices, and technology services.",
        "roles": ["Software Engineer", "Firmware Engineer", "Data Analyst", "QA Engineer", "Security Engineer"],
        "skills": ["Python", "C++", "Java", "Testing", "Linux", "Problem Solving"],
        "languages": ["Python", "C++", "C", "Java", "JavaScript"],
        "tips": ["Show software, device, testing, or automation projects.", "Describe how you reproduced and resolved defects.", "Keep technical claims specific and verifiable."],
        "career_url": "https://jobs.hp.com/",
    },
    {
        "name": "Ericsson",
        "description": "Telecommunications, 5G networks, network software, and connectivity.",
        "roles": ["Software Engineer", "Network Engineer", "Cloud Engineer", "Embedded Engineer", "Security Engineer"],
        "skills": ["Networking", "C++", "Python", "Linux", "Telecommunications", "Testing"],
        "languages": ["C++", "Python", "Java", "C", "JavaScript"],
        "tips": ["Highlight networking, distributed systems, or embedded projects.", "Explain protocols and tools you have actually used.", "Include relevant technical coursework or labs."],
        "career_url": "https://www.ericsson.com/en/careers",
    },
    {
        "name": "Nokia",
        "description": "Telecommunications networks, network infrastructure, and connectivity technology.",
        "roles": ["Software Engineer", "Network Engineer", "Embedded Software Engineer", "Cloud Engineer", "QA Engineer"],
        "skills": ["C++", "Python", "Linux", "Networking", "Testing", "Problem Solving"],
        "languages": ["C++", "C", "Python", "Java", "JavaScript"],
        "tips": ["Show networking, systems, or embedded experience where relevant.", "Describe troubleshooting steps and technical reasoning.", "Be clear about your exact project responsibilities."],
        "career_url": "https://www.nokia.com/about-us/careers/",
    },
    {
        "name": "Red Hat",
        "description": "Enterprise open-source software, Linux, cloud platforms, and automation.",
        "roles": ["Software Engineer", "Linux Engineer", "Cloud Engineer", "Site Reliability Engineer", "Security Engineer"],
        "skills": ["Linux", "Python", "Containers", "Networking", "Automation", "Open Source"],
        "languages": ["Python", "Go", "C", "C++", "Java"],
        "tips": ["Link to useful open-source contributions when available.", "Show Linux, automation, or cloud projects.", "Explain how you collaborate and document technical work."],
        "career_url": "https://www.redhat.com/en/jobs",
    },
    {
        "name": "GitHub",
        "description": "Code hosting, developer collaboration, and software development tools.",
        "roles": ["Software Engineer", "Backend Engineer", "Frontend Developer", "Security Engineer", "Developer Advocate"],
        "skills": ["Git", "GitHub Actions", "JavaScript", "Ruby", "APIs", "Testing"],
        "languages": ["Ruby", "Go", "JavaScript", "TypeScript", "Python"],
        "tips": ["Maintain clear repositories and readable documentation.", "Show collaboration, testing, and maintainable code.", "Link directly to projects that demonstrate your contribution."],
        "career_url": "https://github.careers/",
    },
    {
        "name": "OpenAI",
        "description": "Artificial intelligence research, models, and AI-powered products.",
        "roles": ["Software Engineer", "Research Engineer", "Machine Learning Engineer", "Data Scientist", "Product Engineer"],
        "skills": ["Python", "Machine Learning", "Distributed Systems", "Data Structures", "Evaluation", "Problem Solving"],
        "languages": ["Python", "C++", "JavaScript", "TypeScript", "SQL"],
        "tips": ["Show substantial, reproducible technical work relevant to the role.", "Explain evaluation methods and limitations honestly.", "Distinguish personal contributions from team outcomes."],
        "career_url": "https://openai.com/careers/",
    },
    {
        "name": "Anthropic",
        "description": "AI research and development of AI assistants and related systems.",
        "roles": ["Software Engineer", "Research Engineer", "Machine Learning Engineer", "Security Engineer", "Data Scientist"],
        "skills": ["Python", "Machine Learning", "Evaluation", "Distributed Systems", "Security", "Statistics"],
        "languages": ["Python", "C++", "JavaScript", "TypeScript", "SQL"],
        "tips": ["Present rigorous technical work and reproducible results.", "Discuss evaluation, reliability, or security only with concrete examples.", "Clearly state limitations and your individual contribution."],
        "career_url": "https://www.anthropic.com/careers",
    },
    {
        "name": "Tesla",
        "description": "Electric vehicles, energy storage, manufacturing, and autonomous systems.",
        "roles": ["Software Engineer", "Embedded Engineer", "Manufacturing Engineer", "Data Analyst", "Controls Engineer"],
        "skills": ["Python", "C++", "Embedded Systems", "Automation", "Testing", "Problem Solving"],
        "languages": ["Python", "C++", "JavaScript", "SQL", "C"],
        "tips": ["Highlight practical engineering projects and testing.", "Explain performance or reliability improvements with evidence.", "Tailor your examples to the actual role requirements."],
        "career_url": "https://www.tesla.com/careers",
    },
    {
        "name": "SpaceX",
        "description": "Space launch systems, spacecraft, satellite internet, and aerospace engineering.",
        "roles": ["Software Engineer", "Avionics Engineer", "Embedded Engineer", "Data Engineer", "Manufacturing Engineer"],
        "skills": ["C++", "Python", "Embedded Systems", "Controls", "Testing", "Systems Engineering"],
        "languages": ["C++", "Python", "C", "JavaScript", "MATLAB"],
        "tips": ["Show rigorous engineering projects and validation methods.", "Explain constraints, trade-offs, and failure handling.", "Be precise about your own technical contribution."],
        "career_url": "https://www.spacex.com/careers/",
    },
    {
        "name": "BYD",
        "description": "Electric vehicles, batteries, electronics, and clean energy technology.",
        "roles": ["Software Engineer", "Embedded Engineer", "Battery Engineer", "Data Analyst", "Quality Engineer"],
        "skills": ["C++", "Python", "Embedded Systems", "Testing", "Data Analysis", "Problem Solving"],
        "languages": ["C++", "Python", "C", "Java", "SQL"],
        "tips": ["Highlight relevant software, embedded, or energy-related projects.", "Describe test methods and verified results.", "Use the actual vacancy to tailor your skills."],
        "career_url": "https://www.byd.com/",
    },
    {
        "name": "Booking.com",
        "description": "Online travel booking, marketplace, and travel technology.",
        "roles": ["Software Engineer", "Backend Engineer", "Data Scientist", "Data Analyst", "Product Analyst"],
        "skills": ["Python", "Java", "SQL", "Experimentation", "APIs", "Data Analysis"],
        "languages": ["Python", "Java", "PHP", "JavaScript", "SQL"],
        "tips": ["Show data-informed product or backend projects.", "Explain how you validated results and handled edge cases.", "Connect your technical choices to user needs."],
        "career_url": "https://careers.booking.com/",
    },
    {
        "name": "Walmart Global Tech",
        "description": "Retail technology, e-commerce, supply chain, and data platforms.",
        "roles": ["Software Engineer", "Data Engineer", "Data Analyst", "Cloud Engineer", "Machine Learning Engineer"],
        "skills": ["Java", "Python", "SQL", "Distributed Systems", "Cloud Computing", "Data Analysis"],
        "languages": ["Java", "Python", "JavaScript", "Go", "SQL"],
        "tips": ["Highlight data, retail, logistics, or scalable backend projects.", "Describe the scale of your work only when you can substantiate it.", "Explain your contribution and testing approach."],
        "career_url": "https://tech.walmart.com/content/walmart-global-tech/en_us/careers.html",
    },
]


def search_companies(query: str = "") -> list[dict]:
    """Search curated profiles by company name, description, or supported role."""
    query = query.strip().casefold()
    if not query:
        return COMPANIES

    # Support simple multi-word searches while retaining partial matching.
    terms = [term for term in query.split() if term]
    results = []
    for company in COMPANIES:
        searchable = " ".join([
            company["name"],
            company["description"],
            " ".join(company["roles"]),
            " ".join(company["skills"]),
            " ".join(company["languages"]),
        ]).casefold()

        if all(term in searchable for term in terms):
            results.append(company)

    return results


def get_company(name: str) -> dict | None:
    """Return an exact profile match, case-insensitively."""
    name = name.strip().casefold()
    aliases = {
        "facebook": "meta",
        "jpmorgan chase": "jpmorganchase",
        "jpmorgan chase & co.": "jpmorganchase",
        "walmart": "walmart global tech",
        "hp inc": "hp",
        "hcl": "hcltech",
        "ltimindtree limited": "ltimindtree",
        "tesla inc": "tesla",
        "open ai": "openai",
    }
    name = aliases.get(name, name)
    return next(
        (company for company in COMPANIES if company["name"].casefold() == name),
        None,
    )


@lru_cache(maxsize=1)
def _groq_client():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GROQ_API_KEY is not configured on the server.")
    return Groq(api_key=key)


def analyze_job_description(company: str, role: str, job_description: str) -> dict:
    """Analyze a supplied job description; do not infer official company rules."""
    job_description = job_description.strip()

    if len(job_description) < 50:
        raise ValueError("Paste a job description containing at least 50 characters.")
    if len(job_description) > 15000:
        raise ValueError("The job description must be 15,000 characters or fewer.")

    client = _groq_client()
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0.2,
        max_completion_tokens=1800,
        messages=[
            {
                "role": "system",
                "content": """
You are a careful resume and job-description analyst.
Use only evidence in the supplied job description.
Do not claim to know a company's universal hiring rules.
Never invent facts, qualifications, statistics, or experience.
Return valid JSON only, using this exact structure:
{
  "role_summary": "short summary",
  "required_skills": ["skill explicitly required"],
  "preferred_skills": ["skill described as preferred or desirable"],
  "keywords": ["useful exact terms from the posting"],
  "resume_tips": ["actionable advice based on the posting"],
  "missing_information": ["important requirement unclear in the posting"]
}
Use empty arrays when appropriate. Distinguish explicit requirements
from your interpretations. Do not write a resume for the applicant.
""",
            },
            {
                "role": "user",
                "content": (
                    f"Company: {company[:120]}\n"
                    f"Target role: {role[:120]}\n"
                    f"Job description:\n{job_description}"
                ),
            },
        ],
    )

    raw = (response.choices[0].message.content or "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("The AI returned an invalid response. Please retry.") from exc

    expected = [
        "role_summary",
        "required_skills",
        "preferred_skills",
        "keywords",
        "resume_tips",
        "missing_information",
    ]
    if not isinstance(result, dict):
        raise RuntimeError("The AI returned an unexpected response.")

    for field in expected:
        if field not in result:
            result[field] = "" if field == "role_summary" else []

    result["role_summary"] = str(result["role_summary"])[:2000]
    for field in expected[1:]:
        values = result[field]
        if not isinstance(values, list):
            result[field] = []
        else:
            result[field] = [str(value)[:500] for value in values[:20]]

    return result
