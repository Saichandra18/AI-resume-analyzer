const resumeInput = document.getElementById("resume");
const jobDescriptionInput = document.getElementById(
    "job-description"
);
const analyzeButton = document.getElementById(
    "analyze-button"
);
const resultsSection = document.getElementById("results");
const rewriteResumeButton = document.getElementById(
    "rewrite-resume-button"
);

const rewriteStatus = document.getElementById(
    "rewrite-status"
);

const generateResumeButton = document.getElementById(
    "generate-resume-button"
);

const generationStatus = document.getElementById(
    "generation-status"
);

const experienceLevelInput = document.getElementById(
    "experience-level"
);

const targetPagesInput = document.getElementById(
    "target-pages"
);

const targetJobTitleInput = document.getElementById(
    "target-job-title"
);
const resumeTemplateInput = document.getElementById(
    "resume-template"
);
const downloadResumeButton = document.getElementById(
    "download-resume-button"
);
const downloadPdfButton = document.getElementById(
    "download-pdf-button"
);
const generationDownload = document.getElementById(
    "generation-download"
);
const generationProgress = document.getElementById(
    "generation-progress"
);

const generationProgressFill = document.getElementById(
    "generation-progress-fill"
);

const generationProgressPercent = document.getElementById(
    "generation-progress-percent"
);

const generationStatusMessage = document.getElementById(
    "generation-status-message"
);
const generationATSResults = document.getElementById(
    "generation-ats-results"
);

const generationATSBeforeScore = document.getElementById(
    "generation-ats-before-score"
);

const generationATSAfterScore = document.getElementById(
    "generation-ats-after-score"
);

const generationATSImprovement = document.getElementById(
    "generation-ats-improvement"
);

const generationATSComponentScores = document.getElementById(
    "generation-ats-component-scores"
);

const generationATSNewSkills = document.getElementById(
    "generation-ats-new-skills"
);

const generationATSMissingSkills = document.getElementById(
    "generation-ats-missing-skills"
);

const generationATSNewKeywords = document.getElementById(
    "generation-ats-new-keywords"
);

const generationATSMissingKeywords = document.getElementById(
    "generation-ats-missing-keywords"
);

const generationATSSafetyStatus = document.getElementById(
    "generation-ats-safety-status"
);
const generationValidationResults = document.getElementById(
    "generation-validation-results"
);

const generationValidationStatus = document.getElementById(
    "generation-validation-status"
);

const generationValidationDocxFile = document.getElementById(
    "generation-validation-docx-file"
);

const generationValidationDocxReadable = document.getElementById(
    "generation-validation-docx-readable"
);

const generationValidationDocxText = document.getElementById(
    "generation-validation-docx-text"
);

const generationValidationDocxContent = document.getElementById(
    "generation-validation-docx-content"
);

const generationValidationDocxHeadings = document.getElementById(
    "generation-validation-docx-headings"
);

const generationValidationPdfFile = document.getElementById(
    "generation-validation-pdf-file"
);

const generationValidationPdfReadable = document.getElementById(
    "generation-validation-pdf-readable"
);

const generationValidationPdfText = document.getElementById(
    "generation-validation-pdf-text"
);

const generationValidationPdfContent = document.getElementById(
    "generation-validation-pdf-content"
);

const generationValidationPdfHeadings = document.getElementById(
    "generation-validation-pdf-headings"
);

const generationValidationTargetPages = document.getElementById(
    "generation-validation-target-pages"
);

const generationValidationActualPages = document.getElementById(
    "generation-validation-actual-pages"
);

const generationValidationPageMatch = document.getElementById(
    "generation-validation-page-match"
);

const generationValidationErrors = document.getElementById(
    "generation-validation-errors"
);

const generationValidationWarnings = document.getElementById(
    "generation-validation-warnings"
);
function displayGenerationATSResults(
    atsEvaluation,
    validation = null
) {
    if (!generationATSResults) {
        return;
    }

    if (!atsEvaluation) {
        generationATSResults.style.display = "none";
        return;
    }

    const beforeScore =
        Number(atsEvaluation.before_score ?? 0);

    const afterScore =
        Number(atsEvaluation.after_score ?? 0);

    const improvement =
        Number(atsEvaluation.improvement ?? (
            afterScore - beforeScore
        ));

    generationATSBeforeScore.textContent =
        beforeScore.toFixed(1);

    generationATSAfterScore.textContent =
        afterScore.toFixed(1);

    generationATSImprovement.textContent =
        `${improvement >= 0 ? "+" : ""}${improvement.toFixed(1)}`;

    /*
     * Component score comparison
     */

    const beforeComponents =
        atsEvaluation.before || {};

    const afterComponents =
        atsEvaluation.after || {};

    const componentNames = [
        "skills",
        "experience",
        "qualifications",
        "keywords"
    ];

    generationATSComponentScores.innerHTML = "";

    componentNames.forEach((component) => {
        const before =
            Number(beforeComponents[component] ?? 0);

        const after =
            Number(afterComponents[component] ?? 0);

        const row =
            document.createElement("div");

        row.className =
            "ats-component-score-row";

        row.innerHTML = `
            <span class="ats-component-name">
                ${component.charAt(0).toUpperCase() + component.slice(1)}
            </span>

            <span class="ats-component-before">
                ${before.toFixed(1)}
            </span>

            <span class="ats-component-arrow">
                â†’
            </span>

            <span class="ats-component-after">
                ${after.toFixed(1)}
            </span>
        `;

        generationATSComponentScores.appendChild(row);
    });

    /*
     * Gap analysis
     */

    const gapAnalysis =
        atsEvaluation.gap_analysis || {};

    const newlyMatchedSkills =
        gapAnalysis.newly_matched_skills || [];

    const remainingMissingSkills =
        gapAnalysis.remaining_missing_skills || [];

    const newlyMatchedKeywords =
        gapAnalysis.newly_matched_keywords || [];

    const remainingMissingKeywords =
        gapAnalysis.remaining_missing_keywords || [];

    renderATSList(
        generationATSNewSkills,
        newlyMatchedSkills,
        "No newly matched skills."
    );

    renderATSList(
        generationATSMissingSkills,
        remainingMissingSkills,
        "No remaining missing skills."
    );

    renderATSList(
        generationATSNewKeywords,
        newlyMatchedKeywords,
        "No newly matched keywords."
    );

    renderATSList(
        generationATSMissingKeywords,
        remainingMissingKeywords,
        "No remaining missing keywords."
    );

    /*
     * ATS Safety
     */

    const safetyGate =
        atsEvaluation.document_validation?.ats_safety ||
        validation?.ats_safety;

    if (safetyGate) {
        if (safetyGate.passed) {
            generationATSSafetyStatus.textContent =
                "Passed";

            generationATSSafetyStatus.className =
                "ats-safety-passed";
        } else {
            generationATSSafetyStatus.textContent =
                "Failed";

            generationATSSafetyStatus.className =
                "ats-safety-failed";
        }
    } else {
        generationATSSafetyStatus.textContent =
            "Not evaluated";

        generationATSSafetyStatus.className =
            "";
    }

    generationATSResults.style.display = "block";
}
function displayGenerationValidation(validation) {
    if (!generationValidationResults) {
        return;
    }

    if (!validation) {
        generationValidationResults.style.display = "none";
        return;
    }

    /*
     * Overall validation
     */

    const overallValid =
        validation.valid === true;

    if (generationValidationStatus) {
        generationValidationStatus.textContent =
            overallValid
                ? "Passed"
                : "Failed";

        generationValidationStatus.className =
            overallValid
                ? "validation-passed"
                : "validation-failed";
    }


    /*
     * DOCX validation
     */

    const docx =
        validation.docx || {};

    if (generationValidationDocxFile) {
        generationValidationDocxFile.textContent =
            docx.file_exists ? "Yes" : "No";
    }

    if (generationValidationDocxReadable) {
        generationValidationDocxReadable.textContent =
            docx.readable ? "Yes" : "No";
    }

    if (generationValidationDocxText) {
        generationValidationDocxText.textContent =
            docx.text_present ? "Yes" : "No";
    }

    if (generationValidationDocxContent) {
        generationValidationDocxContent.textContent =
            docx.required_content_present ? "Yes" : "No";
    }

    if (generationValidationDocxHeadings) {
        generationValidationDocxHeadings.textContent =
            docx.standard_headings_present ? "Yes" : "No";
    }


    /*
     * PDF validation
     */

    const pdf =
        validation.pdf || {};

    if (generationValidationPdfFile) {
        generationValidationPdfFile.textContent =
            pdf.file_exists ? "Yes" : "No";
    }

    if (generationValidationPdfReadable) {
        generationValidationPdfReadable.textContent =
            pdf.readable ? "Yes" : "No";
    }

    if (generationValidationPdfText) {
        generationValidationPdfText.textContent =
            pdf.text_present ? "Yes" : "No";
    }

    if (generationValidationPdfContent) {
        generationValidationPdfContent.textContent =
            pdf.required_content_present ? "Yes" : "No";
    }

    if (generationValidationPdfHeadings) {
        generationValidationPdfHeadings.textContent =
            pdf.standard_headings_present ? "Yes" : "No";
    }


    /*
     * PDF page count
     */

    if (generationValidationTargetPages) {
        generationValidationTargetPages.textContent =
            pdf.target_pages ?? "--";
    }

    if (generationValidationActualPages) {
        generationValidationActualPages.textContent =
            pdf.actual_pages ?? "--";
    }

    if (generationValidationPageMatch) {
        generationValidationPageMatch.textContent =
            pdf.page_count_match
                ? "Yes"
                : "No";
    }


    /*
     * Validation errors
     */

    if (generationValidationErrors) {
        generationValidationErrors.innerHTML = "";

        const errors =
            Array.isArray(validation.errors)
                ? validation.errors
                : [];

        if (errors.length === 0) {
            const item =
                document.createElement("li");

            item.textContent =
                "No validation errors.";

            generationValidationErrors.appendChild(item);
        } else {
            errors.forEach((error) => {
                const item =
                    document.createElement("li");

                item.textContent = error;

                generationValidationErrors.appendChild(item);
            });
        }
    }


    /*
     * Validation warnings
     */

    if (generationValidationWarnings) {
        generationValidationWarnings.innerHTML = "";

        const warnings =
            Array.isArray(validation.warnings)
                ? validation.warnings
                : [];

        if (warnings.length === 0) {
            const item =
                document.createElement("li");

            item.textContent =
                "No validation warnings.";

            generationValidationWarnings.appendChild(item);
        } else {
            warnings.forEach((warning) => {
                const item =
                    document.createElement("li");

                item.textContent = warning;

                generationValidationWarnings.appendChild(item);
            });
        }
    }


    /*
     * Show validation results
     */

    generationValidationResults.style.display = "block";
}

function renderATSList(
    container,
    items,
    emptyMessage
) {
    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        const li =
            document.createElement("li");

        li.textContent = emptyMessage;

        container.appendChild(li);

        return;
    }

    items.forEach((item) => {
        const li =
            document.createElement("li");

        li.textContent = item;

        container.appendChild(li);
    });
}

function updateGenerationProgress(
    percent,
    message,
    activeStep = null,
    completedSteps = []
) {
    if (!generationProgress) {
        return;
    }

    generationProgress.style.display = "block";

    const safePercent = Math.max(
        0,
        Math.min(100, Number(percent) || 0)
    );

    if (generationProgressFill) {
        generationProgressFill.style.width =
            `${safePercent}%`;
    }

    if (generationProgressPercent) {
        generationProgressPercent.textContent =
            `${safePercent}%`;
    }

    if (generationStatusMessage) {
        generationStatusMessage.textContent =
            message || "";
    }

    const steps = [
        "prepare",
        "optimize",
        "generate",
        "validate",
        "complete"
    ];

    steps.forEach((stepName) => {
        const step = document.getElementById(
            `generation-step-${stepName}`
        );

        if (!step) {
            return;
        }

        const icon = step.querySelector(
            ".generation-step-icon"
        );

        step.classList.remove(
            "active",
            "completed"
        );

        if (completedSteps.includes(stepName)) {
            step.classList.add("completed");

            if (icon) {
                icon.textContent = "âœ“";
            }

            return;
        }

        if (stepName === activeStep) {
            step.classList.add("active");

            if (icon) {
                icon.textContent = "â—";
            }

            return;
        }

        if (icon) {
            icon.textContent = "â—‹";
        }
    });
}
function displayScoreResults(data) {
    const atsScoreValue = document.getElementById(
        "ats-score-value"
    );

    const skillsScore = document.getElementById(
        "skills-score"
    );

    const experienceScore = document.getElementById(
        "experience-score"
    );

    const qualificationsScore = document.getElementById(
        "qualifications-score"
    );

    const keywordsScore = document.getElementById(
        "keywords-score"
    );

    const componentScores = data.component_scores || {};

    atsScoreValue.textContent = data.ats_score ?? 0;

    skillsScore.textContent =
        componentScores.skills != null
            ? `${Math.round(componentScores.skills)} / 100`
            : "N/A";

    experienceScore.textContent =
        componentScores.experience != null
            ? `${Math.round(componentScores.experience)} / 100`
            : "N/A";

    qualificationsScore.textContent =
        componentScores.qualifications != null
            ? `${Math.round(componentScores.qualifications)} / 100`
            : "N/A";

    keywordsScore.textContent =
        componentScores.keywords != null
            ? `${Math.round(componentScores.keywords)} / 100`
            : "N/A";

    resultsSection.style.display = "block";

    const scoreBreakdown = document.getElementById(
        "score-breakdown-list"
    );

    scoreBreakdown.innerHTML = "";

    const explanation =
        data.score_explanation || {};

    const components =
        explanation.components || {};

    const componentLabels = {
        skills: "Skills",
        experience: "Experience",
        qualifications: "Qualifications",
        keywords: "Keywords"
    };

    Object.entries(componentLabels).forEach(
        ([key, label]) => {
            const component = components[key];

            if (!component || component.score == null) {
                return;
            }

            const item = document.createElement("div");

            item.className = "score-breakdown-item";

            const title = document.createElement("h3");

            title.textContent = label;

            const details = document.createElement("p");

            details.textContent =
                `Score: ${Math.round(component.score)}% | ` +
                `Weight: ${Math.round(component.weight)}% | ` +
                `Contribution: ${component.contribution} points`;

            item.appendChild(title);
            item.appendChild(details);

            scoreBreakdown.appendChild(item);
        }
    );
}

function displayResumeQuality(data) {
    const resume_quality = data.resume_quality || {};

    const scoreElement = document.getElementById(
        "resume-quality-score"
    );

    const componentsElement = document.getElementById(
        "resume-quality-components"
    );

    const missingElement = document.getElementById(
        "resume-quality-missing"
    );

    const optionalElement = document.getElementById(
        "resume-quality-optional"
    );

    scoreElement.textContent =
        resume_quality.score != null
            ? `${resume_quality.score} / 100`
            : "N/A";

    componentsElement.innerHTML = "";

    const components =
        resume_quality.components || {};

    Object.entries(components).forEach(
        ([name, component]) => {
            const item = document.createElement("div");

            item.className =
                "resume-quality-component";

            const label = document.createElement("span");

        const labelText = {
            name: "Name",
            email: "Email",
            phone: "Phone",
            skills: "Skills",
            education: "Education",
            experience: "Experience",
            projects: "Projects",
            certifications: "Certifications"
        };

label.textContent =
    labelText[name] || name;

            const status = document.createElement("span");

            status.textContent =
                component.present
                    ? `âœ“ ${component.score}`
                    : "Missing";

            item.appendChild(label);
            item.appendChild(status);

            componentsElement.appendChild(item);
        }
    );

    missingElement.innerHTML = "";

    const missingSections =
        resume_quality.missing_sections || [];

    if (missingSections.length === 0) {
        const item = document.createElement("li");

        item.textContent =
            "No required sections are missing.";

        missingElement.appendChild(item);
    } else {
        missingSections.forEach((section) => {
            const item = document.createElement("li");

            item.textContent = section;

            missingElement.appendChild(item);
        });
    }

    optionalElement.innerHTML = "";

    const optionalSections =
        resume_quality.optional_sections || {};

    Object.entries(optionalSections).forEach(
        ([name, section]) => {
            const item = document.createElement("li");

            item.textContent =
                section.present
                    ? `${name}: Present`
                    : `${name}: Not detected`;

            optionalElement.appendChild(item);
        }
    );

    /*
     * Resume completeness fields
     */

    const fields = [
        "name",
        "email",
        "phone",
        "skills",
        "education",
        "experience",
        "projects",
        "certifications"
    ];

    fields.forEach((field) => {
        const element = document.getElementById(
            `resume-quality-${field}`
        );

        if (!element) {
            return;
        }

        if (field === "certifications") {
            const certification =
                resume_quality.optional_sections?.certifications;

            element.textContent =
                certification?.present
                    ? "Present"
                    : "Not detected";

            return;
        }

        const component =
            resume_quality.components?.[field];

        element.textContent =
            component?.present
                ? "Present"
                : "Not detected";
    });
}

function displayResumeContentQuality(data) {
    const resume_content_quality =
        data.resume_content_quality || data.content_quality || {};

    const scoreElement = document.getElementById(
        "resume-content-quality-score"
    );

    const signalsElement = document.getElementById(
        "resume-content-quality-signals"
    );

    const warningsElement = document.getElementById(
        "resume-content-quality-warnings"
    );

    const recommendationsElement = document.getElementById(
        "resume-content-quality-recommendations"
    );

    if (!scoreElement) {
        return;
    }

    scoreElement.textContent =
        resume_content_quality.score ?? 0;

    const signals =
        resume_content_quality.signals || {};

    const signalLabels = {
        contact_information:
            "content-quality-contact-information",

        quantified_achievements:
            "content-quality-quantified-achievements",

        action_oriented_experience:
            "content-quality-action-oriented-experience",

        project_description:
            "content-quality-project-description"
    };

    Object.entries(signalLabels).forEach(
        ([name, elementId]) => {
            const element = document.getElementById(
                elementId
            );

            if (!element) {
                return;
            }

            const present = signals[name];

            element.textContent = present
                ? "Present"
                : "Not detected";
        }
    );

    warningsElement.innerHTML = "";

    const warnings =
        Array.isArray(resume_content_quality.warnings)
            ? resume_content_quality.warnings
            : [];

    if (warnings.length === 0) {
        const item = document.createElement("li");

        item.textContent =
            "No content-quality warnings.";

        warningsElement.appendChild(item);
    } else {
        warnings.forEach((warning) => {
            const item = document.createElement("li");

            item.textContent = warning;

            warningsElement.appendChild(item);
        });
    }

    recommendationsElement.innerHTML = "";

    const recommendations =
        Array.isArray(
            resume_content_quality.recommendations
        )
            ? resume_content_quality.recommendations
            : [];

    if (recommendations.length === 0) {
        const item = document.createElement("li");

        item.textContent =
            "No content-quality recommendations.";

        recommendationsElement.appendChild(item);
    } else {
        recommendations.forEach(
            (recommendation) => {
                const item =
                    document.createElement("li");

                item.textContent = recommendation;

                recommendationsElement.appendChild(
                    item
                );
            }
        );
    }
}

function formatLabel(value) {
    if (!value) {
        return "";
    }

    return String(value)
        .replace(/[_-]+/g, " ")
        .replace(/\s+/g, " ")
        .trim()
        .replace(/\b\w/g, (character) =>
            character.toUpperCase()
        );
}

function displayImprovementSuggestions(data) {
    const container = document.getElementById(
        "resume-improvement-suggestions"
    );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    const suggestions =
        Array.isArray(data.improvement_suggestions)
            ? data.improvement_suggestions
            : [];

    if (suggestions.length === 0) {
        const message = document.createElement("p");

        message.textContent =
            "No improvement suggestions available.";

        container.appendChild(message);

        return;
    }

    suggestions.forEach((suggestion) => {
        const card = document.createElement("div");

        card.className =
            "resume-improvement-suggestion";

        const header = document.createElement("div");

        header.className =
            "resume-improvement-header";

        const type = document.createElement("strong");

        type.textContent =
            `${formatLabel(
                suggestion.type || "Improvement"
            )} â€¢ ${
                suggestion.priority || "medium"
            }`;

        header.appendChild(type);

        card.appendChild(header);

        if (suggestion.current_text) {
            const currentLabel =
                document.createElement("strong");

            currentLabel.textContent =
                "Current Text";

            const currentText =
                document.createElement("p");

            currentText.textContent =
                suggestion.current_text;

            card.appendChild(currentLabel);
            card.appendChild(currentText);
        }

        const suggestionLabel =
            document.createElement("strong");

        suggestionLabel.textContent =
            "How to Improve";

        const suggestionText =
            document.createElement("p");

        suggestionText.textContent =
            suggestion.suggestion ||
            "No improvement suggestion available.";

        card.appendChild(suggestionLabel);
        card.appendChild(suggestionText);

        const reasonLabel =
            document.createElement("strong");

        reasonLabel.textContent =
            "Why";

        const reasonText =
            document.createElement("p");

        reasonText.textContent =
            suggestion.reason ||
            "No reason provided.";

        card.appendChild(reasonLabel);
        card.appendChild(reasonText);

        container.appendChild(card);
    });
}

function displayTailoringPlan(data) {
    const plan = data.tailoring_plan || {};

    const prioritiesContainer = document.getElementById(
        "tailoring-priorities"
    );
    const summaryContainer = document.getElementById(
        "tailoring-summary"
    );
    const skillsContainer = document.getElementById(
        "tailoring-skills"
    );
    const experienceContainer = document.getElementById(
        "tailoring-experience"
    );
    const keywordsContainer = document.getElementById(
        "tailoring-keywords"
    );
    const qualificationsContainer = document.getElementById(
        "tailoring-qualifications"
    );
    const warningsContainer = document.getElementById(
        "tailoring-warnings"
    );

    const sections = [
        {
            container: prioritiesContainer,
            items: plan.priorities || [],
        },
        {
            container: summaryContainer,
            items: plan.summary || [],
        },
        {
            container: skillsContainer,
            items: plan.skills || [],
        },
        {
            container: experienceContainer,
            items: plan.experience || [],
        },
        {
            container: keywordsContainer,
            items: plan.keywords || [],
        },
        {
            container: qualificationsContainer,
            items: plan.qualifications || [],
        },
    ];

    const renderItems = (container, items) => {
        if (!container) {
            return;
        }

        container.innerHTML = "";

        if (!items || items.length === 0) {
            return;
        }

        items.forEach((item) => {
            const card = document.createElement("div");

            card.className =
                "resume-tailoring-item";

            const header = document.createElement("div");

            header.className =
                "resume-tailoring-header";

            if (item.action) {
                const action = document.createElement("strong");

                action.textContent = item.action;

                header.appendChild(action);
            }

            if (item.priority) {
                const priority =
                    document.createElement("span");

                priority.className =
                    "resume-tailoring-priority";

                priority.textContent =
                    item.priority;

                header.appendChild(priority);
            }

            card.appendChild(header);

            if (item.recommendation) {
                const recommendation =
                    document.createElement("p");

                recommendation.textContent =
                    item.recommendation;

                card.appendChild(recommendation);
            }

            container.appendChild(card);
        });
    };

    sections.forEach((section) => {
        renderItems(
            section.container,
            section.items
        );

        const sectionWrapper =
            section.container?.closest(
                ".resume-tailoring-section"
            );

        if (sectionWrapper) {
            sectionWrapper.style.display =
                section.items.length > 0
                    ? ""
                    : "none";
        }
    });

    if (!warningsContainer) {
        return;
    }

    warningsContainer.innerHTML = "";

    const warnings = plan.warnings || [];

    if (warnings.length === 0) {
        const sectionWrapper =
            warningsContainer.closest(
                ".resume-tailoring-section"
            );

        if (sectionWrapper) {
            sectionWrapper.style.display = "none";
        }

        return;
    }

    const warningSection =
        warningsContainer.closest(
            ".resume-tailoring-section"
        );

    if (warningSection) {
        warningSection.style.display = "";
    }

    warnings.forEach((warning) => {
        const paragraph =
            document.createElement("p");

        paragraph.textContent = warning;

        warningsContainer.appendChild(paragraph);
    });
}

function displayMatchResults(data) {
    const matchSections = [
        {
            elementId: "matched-skills",
            values: data.matched_skills,
            emptyMessage: "No matched skills."
        },
        {
            elementId: "missing-skills",
            values: data.missing_skills,
            emptyMessage: "No missing skills."
        },
        {
            elementId: "matched-qualifications",
            values: data.matched_qualifications,
            emptyMessage: "No matched qualifications."
        },
        {
            elementId: "missing-qualifications",
            values: data.missing_qualifications,
            emptyMessage: "No missing qualifications."
        },
        {
            elementId: "matched-keywords",
            values: groupMatchedKeywords(
                Array.isArray(data.matched_keywords)
                    ? data.matched_keywords
                    : []
            ),
            emptyMessage: "No matched keywords."
        },
        {
            elementId: "missing-keywords",
            values: data.missing_keywords,
            emptyMessage: "No missing keywords."
        }
    ];

    matchSections.forEach((section) => {
        const element = document.getElementById(
            section.elementId
        );

        element.innerHTML = "";

        const values = Array.isArray(section.values)
            ? section.values
            : [];

        if (values.length === 0) {
            const item = document.createElement("li");

            item.textContent = section.emptyMessage;

            element.appendChild(item);

            return;
        }

        values.forEach((value) => {
            const item = document.createElement("li");

            item.textContent = value;

            element.appendChild(item);
        });
    });
}

function groupMatchedKeywords(keywords) {
    const groups = [
        {
            label: "Artificial Intelligence (AI)",
            terms: [
                "artificial intelligence",
                "ai"
            ]
        },
        {
            label: "Machine Learning (ML)",
            terms: [
                "machine learning",
                "ml"
            ]
        },
        {
            label: "Generative AI (GenAI)",
            terms: [
                "generative ai",
                "genai"
            ]
        },
        {
            label: "Large Language Models (LLM)",
            terms: [
                "large language model",
                "large language models",
                "llm",
                "llms"
            ]
        },
        {
            label: "Retrieval Augmented Generation (RAG)",
            terms: [
                "retrieval augmented generation",
                "rag"
            ]
        },
        {
            label: "Neural Networks",
            terms: [
                "neural network",
                "neural networks"
            ]
        },
        {
            label: "CI/CD",
            terms: [
                "ci cd",
                "ci",
                "cd"
            ]
        }
    ];

    const normalizedKeywords = new Set(
        keywords.map((keyword) =>
            keyword.trim().toLowerCase()
        )
    );

    const grouped = [];

    groups.forEach((group) => {
        const matched = group.terms.some((term) =>
            normalizedKeywords.has(term)
        );

        if (matched) {
            grouped.push(group.label);
        }
    });

    const groupedTerms = new Set(
        groups.flatMap((group) => group.terms)
    );

    keywords.forEach((keyword) => {
        const normalized = keyword.trim().toLowerCase();

        if (!groupedTerms.has(normalized)) {
            grouped.push(keyword);
        }
    });

    return grouped;
}

function groupInsightValues(values, sectionType) {
    if (!Array.isArray(values) || values.length === 0) {
        return [];
    }

    const groups = [
        {
            label: "MLOps & Production",
            terms: [
                "machine learning operations",
                "mlops",
                "llmops",
                "model deployment",
                "model monitoring"
            ],
            canonical: {
                "machine learning operations":
                    "Machine Learning Operations",
                "mlops": "MLOps",
                "llmops": "LLMOps",
                "model deployment": "Model Deployment",
                "model monitoring": "Model Monitoring"
            }
        },
        {
            label: "Model Evaluation",
            terms: [
                "model validation",
                "model evaluation",
                "model testing"
            ],
            canonical: {
                "model validation": "Model Validation",
                "model evaluation": "Model Evaluation",
                "model testing": "Model Testing"
            }
        },
        {
            label: "AI/ML Foundation",
            terms: [
                "artificial intelligence",
                "ai",
                "machine learning",
                "ml",
                "generative ai",
                "genai",
                "large language models",
                "large language model",
                "llms",
                "llm",
                "retrieval augmented generation",
                "rag",
                "neural networks",
                "neural network",
                "deep learning"
            ],
            canonical: {
                "artificial intelligence":
                    "Artificial Intelligence (AI)",
                "ai":
                    "Artificial Intelligence (AI)",
                "machine learning":
                    "Machine Learning (ML)",
                "ml":
                    "Machine Learning (ML)",
                "generative ai":
                    "Generative AI (GenAI)",
                "genai":
                    "Generative AI (GenAI)",
                "large language models":
                    "Large Language Models (LLM)",
                "large language model":
                    "Large Language Models (LLM)",
                "llms":
                    "Large Language Models (LLM)",
                "llm":
                    "Large Language Models (LLM)",
                "retrieval augmented generation":
                    "Retrieval Augmented Generation (RAG)",
                "rag":
                    "Retrieval Augmented Generation (RAG)",
                "neural networks":
                    "Neural Networks",
                "neural network":
                    "Neural Networks",
                "deep learning":
                    "Deep Learning"
            }
        },
        {
            label: "Engineering & Development",
            terms: [
                "python",
                "java",
                "javascript",
                "typescript",
                "c++",
                "ci/cd",
                "ci cd",
                "ci",
                "cd",
                "software development"
            ],
            canonical: {
                "python": "Python",
                "java": "Java",
                "javascript": "JavaScript",
                "typescript": "TypeScript",
                "c++": "C++",
                "ci/cd": "CI/CD",
                "ci cd": "CI/CD",
                "ci": "CI/CD",
                "cd": "CI/CD",
                "software development":
                    "Software Development"
            }
        }
    ];

    const normalize = (text) =>
        text
            .toString()
            .trim()
            .toLowerCase()
            .replace(/[()]/g, "")
            .replace(/\s+/g, " ");

    const getItemText = (value) =>
        normalize(
            value?.item ||
            value?.description ||
            value?.recommendation ||
            value ||
            ""
        );

    const grouped = [];
    const usedIndexes = new Set();

    groups.forEach((group) => {
        const canonicalItems = [];
        const seenCanonical = new Set();

        values.forEach((value, index) => {
            if (usedIndexes.has(index)) {
                return;
            }

            const text = getItemText(value);

            const matchedTerm = group.terms.find((term) =>
                text.includes(normalize(term))
            );

            if (!matchedTerm) {
                return;
            }

            usedIndexes.add(index);

            const canonicalItem =
                group.canonical[matchedTerm] || matchedTerm;

            const normalizedCanonical =
                normalize(canonicalItem);

            if (!seenCanonical.has(normalizedCanonical)) {
                seenCanonical.add(normalizedCanonical);
                canonicalItems.push(canonicalItem);
            }
        });

        if (canonicalItems.length === 0) {
            return;
        }

        let description;

        if (sectionType === "strengths") {
            description =
                `Strong coverage across ` +
                `${canonicalItems.join(", ")}.`;
        } else if (sectionType === "weaknesses") {
            description =
                `Consider strengthening ` +
                `${group.label} with ` +
                `${canonicalItems.join(", ")} ` +
                `where applicable.`;
        } else {
            description =
                `Highlight relevant ` +
                `${group.label.toLowerCase()} experience, ` +
                `including ${canonicalItems.join(", ")}, ` +
                `if applicable.`;
        }

        grouped.push({
            type: "group",
            item: group.label,
            description: description
        });
    });

    /*
     * Preserve non-grouped insights such as experience
     * and qualifications.
     */
    values.forEach((value, index) => {
        if (!usedIndexes.has(index)) {
            grouped.push(value);
        }
    });

    return grouped;
}

function displayInsightResults(data) {
    const insightSections = [
        {
            elementId: "strengths-list",
            values: groupInsightValues(
                data.strengths,
                "strengths"
            ),
            emptyMessage: "No strengths identified."
        },
        {
            elementId: "weaknesses-list",
            values: groupInsightValues(
                data.weaknesses,
                "weaknesses"
            ),
            emptyMessage: "No areas to improve identified."
        },
        {
            elementId: "recommendations-list",
            values: groupInsightValues(
                data.recommendations,
                "recommendations"
            ),
            emptyMessage: "No recommendations available."
        }
    ];

    insightSections.forEach((section) => {
        const element = document.getElementById(
            section.elementId
        );

        element.innerHTML = "";

        const values = Array.isArray(section.values)
            ? section.values
            : [];

        if (values.length === 0) {
            const item = document.createElement("li");

            item.textContent = section.emptyMessage;

            element.appendChild(item);

            return;
        }

        values.forEach((value) => {
            const item = document.createElement("li");

            if (typeof value === "object" && value !== null) {
                item.textContent =
                    value.description ||
                    value.recommendation ||
                    value.item ||
                    "No insight available.";
            } else {
                item.textContent = value;
            }

            element.appendChild(item);
        });
    });
}

analyzeButton.addEventListener("click", async () => {
    const resumeFile = resumeInput.files[0];
    const jobDescription = jobDescriptionInput.value.trim();

    if (!resumeFile) {
        alert("Please select a resume.");
        return;
    }

    if (!jobDescription) {
        alert("Please enter a job description.");
        return;
    }

    const formData = new FormData();

    formData.append("resume", resumeFile);
    formData.append(
        "job_description",
        jobDescription
    );

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing...";

    try {
        const response = await fetch(
            "/api/analyze",
            {
                method: "POST",
                body: formData,
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "Analysis failed."
            );
        }

        console.log("ATS analysis result:", data);

        window.atsAnalysisResult = data;

        displayScoreResults(data);
        displayMatchResults(data);
        displayInsightResults(data);
        displayResumeQuality(data);
        displayResumeContentQuality(data);
        displayImprovementSuggestions(data);
        displayTailoringPlan(data);

    } catch (error) {
        console.error(
            "ATS analysis error:",
            error
        );

        alert(error.message);

    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze Resume";
    }
});
function displayRewriteResults(data) {
    const resultsContainer = document.getElementById(
        "rewrite-results"
    );

    if (!resultsContainer) {
        return;
    }

    resultsContainer.style.display = "block";

    /*
     * Validation
     */

    const validation =
        data.validation || {};

    const groundingStatus =
        document.getElementById(
            "rewrite-grounding-status"
        );

    const meaningPreserved =
        document.getElementById(
            "rewrite-meaning-preserved"
        );

    const validationWarnings =
        document.getElementById(
            "rewrite-validation-warnings"
        );

    groundingStatus.textContent =
        validation.grounding_status ||
        "unverified";

    meaningPreserved.textContent =
        validation.meaning_preserved
            ? "Yes"
            : "No";

    validationWarnings.innerHTML = "";

    const warnings =
        Array.isArray(
            validation.unsupported_claims
        )
            ? validation.unsupported_claims
            : [];

    if (warnings.length === 0) {
        const item =
            document.createElement("li");

        item.textContent =
            "No unsupported claims detected.";

        validationWarnings.appendChild(item);
    } else {
        warnings.forEach((warning) => {
            const item =
                document.createElement("li");

            item.textContent = warning;

            validationWarnings.appendChild(item);
        });
    }


    /*
     * Summary
     */

    const summary =
        data.summary || {};

    const summaryOriginal =
        document.getElementById(
            "rewrite-summary-original"
        );

    const summaryRewritten =
        document.getElementById(
            "rewrite-summary-rewritten"
        );

    summaryOriginal.textContent =
        summary.original || "No summary detected.";

    summaryRewritten.textContent =
        summary.rewritten || "No rewritten summary available.";


    /*
     * Experience
     */

    const experienceContainer =
        document.getElementById(
            "rewrite-experience-list"
        );

    experienceContainer.innerHTML = "";

    const experience =
        Array.isArray(data.experience)
            ? data.experience
            : [];

    experience.forEach((item) => {
        const card =
            document.createElement("div");

        card.className =
            "rewrite-comparison";

        const original =
            document.createElement("div");

        const originalHeading =
            document.createElement("h3");

        originalHeading.textContent =
            "Original";

        const originalText =
            document.createElement("p");

        originalText.textContent =
            item.original || "--";

        original.appendChild(
            originalHeading
        );

        original.appendChild(
            originalText
        );


        const rewritten =
            document.createElement("div");

        const rewrittenHeading =
            document.createElement("h3");

        rewrittenHeading.textContent =
            "Rewritten";

        const rewrittenText =
            document.createElement("p");

        rewrittenText.textContent =
            item.rewritten || "--";

        rewritten.appendChild(
            rewrittenHeading
        );

        rewritten.appendChild(
            rewrittenText
        );

        card.appendChild(original);
        card.appendChild(rewritten);

        experienceContainer.appendChild(card);
    });


    /*
     * Projects
     */

    const projectsContainer =
        document.getElementById(
            "rewrite-projects-list"
        );

    projectsContainer.innerHTML = "";

    const projects =
        Array.isArray(data.projects)
            ? data.projects
            : [];

    projects.forEach((item) => {
        const card =
            document.createElement("div");

        card.className =
            "rewrite-comparison";

        const original =
            document.createElement("div");

        const originalHeading =
            document.createElement("h3");

        originalHeading.textContent =
            "Original";

        const originalText =
            document.createElement("p");

        originalText.textContent =
            item.original || "--";

        original.appendChild(
            originalHeading
        );

        original.appendChild(
            originalText
        );


        const rewritten =
            document.createElement("div");

        const rewrittenHeading =
            document.createElement("h3");

        rewrittenHeading.textContent =
            "Rewritten";

        const rewrittenText =
            document.createElement("p");

        rewrittenText.textContent =
            item.rewritten || "--";

        rewritten.appendChild(
            rewrittenHeading
        );

        rewritten.appendChild(
            rewrittenText
        );

        card.appendChild(original);
        card.appendChild(rewritten);

        projectsContainer.appendChild(card);
    });


    /*
     * Skills
     */

    const skills =
        data.skills || {};

    const originalSkills =
        document.getElementById(
            "rewrite-skills-original"
        );

    const rewrittenSkills =
        document.getElementById(
            "rewrite-skills-rewritten"
        );

    originalSkills.innerHTML = "";
    rewrittenSkills.innerHTML = "";

    const originalSkillList =
        Array.isArray(skills.original)
            ? skills.original
            : [];

    const rewrittenSkillList =
        Array.isArray(skills.rewritten)
            ? skills.rewritten
            : [];

    originalSkillList.forEach((skill) => {
        const item =
            document.createElement("li");

        item.textContent = skill;

        originalSkills.appendChild(item);
    });

    rewrittenSkillList.forEach((skill) => {
        const item =
            document.createElement("li");

        item.textContent = skill;

        rewrittenSkills.appendChild(item);
    });
}
rewriteResumeButton.addEventListener("click", async () => {
    if (!window.atsAnalysisResult) {
        alert("Please analyze your resume first.");
        return;
    }

    const analysis = window.atsAnalysisResult;

    const resumeData =
        analysis.resume_data || {};

    const tailoringPlan =
        analysis.tailoring_plan || {};

    const jobDescription =
        jobDescriptionInput.value.trim();

    const payload = {
        resume_text: analysis.resume_text || "",
        resume_data: resumeData,
        tailoring_plan: tailoringPlan,
        job_description: jobDescription,
        experience: resumeData.experience || [],
        projects: resumeData.projects || [],
        skills: resumeData.skills || [],
    };

    rewriteResumeButton.disabled = true;
    rewriteResumeButton.textContent =
        "Rewriting...";

    rewriteStatus.textContent =
        "AI is rewriting your resume...";

    try {
        const response = await fetch(
            "/api/resume/rewrite",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message ||
                "Resume rewrite failed."
            );
        }

        console.log(
            "Resume rewrite result:",
            data
        );

        window.resumeRewriteResult =
            data.rewrite;

        displayRewriteResults(
            data.rewrite
        );

        rewriteStatus.textContent =
            "Resume rewrite completed successfully.";

    } catch (error) {
        console.error(
            "Resume rewrite error:",
            error
        );

        rewriteStatus.textContent =
            error.message ||
            "Could not rewrite resume.";

    } finally {
        rewriteResumeButton.disabled = false;
        rewriteResumeButton.textContent =
            "Rewrite Resume";
    }
});
generateResumeButton.addEventListener(
    "click",
    async () => {
        if (!window.atsAnalysisResult) {
            alert(
                "Please analyze your resume first."
            );
            return;
        }

        const analysis =
            window.atsAnalysisResult;

        const resumeData =
            analysis.resume_data || {};

        const tailoringPlan =
            analysis.tailoring_plan || {};

        const jobDescription =
            jobDescriptionInput.value.trim();

        if (!jobDescription) {
            alert(
                "Please enter a job description."
            );
            return;
        }

        const targetPages =
            Number(targetPagesInput.value);

        const payload = {
            resume_text:
                analysis.resume_text || "",

            resume_data:
                resumeData,

            job_description:
                jobDescription,

            ats_result:
                analysis,

            resume_quality:
                analysis.resume_quality || {},

            content_quality:
                analysis.resume_content_quality || analysis.content_quality || {},

            improvement_suggestions:
                analysis.improvement_suggestions || [],

            tailoring_plan:
                tailoringPlan,

            experience_level:
                experienceLevelInput.value,

            target_pages:
                targetPages,

            target_job_title:
                targetJobTitleInput.value.trim() ||
                null,

            template:
                resumeTemplateInput.value
        };

        generateResumeButton.disabled = true;

        generateResumeButton.textContent =
            "Generating...";

        updateGenerationProgress(
            10,
            "Preparing your resume data...",
            "prepare"
        );

        try {
            updateGenerationProgress(
                25,
                "Optimizing resume content...",
                "optimize",
                ["prepare"]
            );
            const response = await fetch(
                "/api/resume/generate",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        payload
                    )
                }
            );

            const data =
                await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message ||
                    "Resume generation failed."
                );
            }

            console.log(
                "Optimized resume generation result:",
                data
            );
            updateGenerationProgress(
                75,
                "Validating generated documents...",
                "validate",
                [
                    "prepare",
                    "optimize",
                    "generate"
                ]
            );

            window.resumeGenerationResult =
                data;

            displayGenerationATSResults(
                data.ats_evaluation,
                data.document_validation
            );

            displayGenerationValidation(
                data.document_validation
            );

            updateGenerationProgress(
                100,
                "Optimized resume generated successfully.",
                "complete",
                [
                    "prepare",
                    "optimize",
                    "generate",
                    "validate"
                ]
            );

            generationDownload.style.display = "block";

        } catch (error) {
            console.error(
                "Resume generation error:",
                error
            );

            generationStatus.textContent =
                error.message ||
                "Could not generate optimized resume.";

        } finally {
            generateResumeButton.disabled =
                false;

            generateResumeButton.textContent =
                "Generate Optimized Resume";
        }
    }
);

downloadResumeButton.addEventListener(
    "click",
    () => {
        const result =
            window.resumeGenerationResult;

        if (!result || !result.document_path) {
            alert(
                "Please generate an optimized resume first."
            );
            return;
        }

        const filename =
            result.document_path
                .split(/[\\/]/)
                .pop();

        if (!filename) {
            alert(
                "The generated DOCX file could not be identified."
            );
            return;
        }

        const downloadUrl =
            `/api/resume/download?filename=${encodeURIComponent(
                filename
            )}`;

        window.location.href =
            downloadUrl;
    }
);

downloadPdfButton.addEventListener(
    "click",
    () => {
        const result =
            window.resumeGenerationResult;

        if (!result || !result.pdf_path) {
            alert(
                "Please generate an optimized resume first."
            );
            return;
        }

        const filename =
            result.pdf_path
                .split(/[\\/]/)
                .pop();

        if (!filename) {
            alert(
                "The generated PDF file could not be identified."
            );
            return;
        }

        const downloadUrl =
            `/api/resume/download?filename=${encodeURIComponent(
                filename
            )}`;

        window.location.href =
            downloadUrl;
    }
);
