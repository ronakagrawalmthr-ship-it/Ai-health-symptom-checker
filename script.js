/**
 * AI Health Symptom Checker - Frontend JavaScript
 * Simplified version with reliable element handling
 */

(function() {
    'use strict';

    // Language settings
    let currentLanguage = 'en';
    let selectedLanguage = null;

    // Medical conditions database with expanded symptoms
    const medicalConditions = [
        // Common symptoms
        { name: 'Fever', keywords: ['fever', 'high temperature', 'febrile', 'feeling hot', 'chills', 'rigors'] },
        { name: 'Cold & Flu', keywords: ['cold', 'flu', 'cough', 'runny nose', 'nasal congestion', 'sore throat', 'flu symptoms'] },
        { name: 'Headache', keywords: ['headache', 'head pain', 'migraine', 'head ache', 'throbbing head'] },
        { name: 'Stomach Pain', keywords: ['stomach pain', 'abdominal pain', 'belly pain', 'stomach ache', 'tummy pain'] },
        { name: 'Nausea', keywords: ['nausea', 'nauseous', 'feeling sick', 'queasy', 'sick to stomach'] },
        { name: 'Chest Pain', keywords: ['chest pain', 'chest discomfort', 'heart pain', 'tight chest'] },
        { name: 'Shortness of Breath', keywords: ['shortness of breath', 'breathlessness', 'difficulty breathing', 'breathing difficulty', 'dyspnea'] },
        // More common conditions
        { name: 'Cough', keywords: ['cough', 'coughing', 'dry cough', 'wet cough', 'productive cough'] },
        { name: 'Fatigue', keywords: ['fatigue', 'tiredness', 'exhaustion', 'feeling tired', 'weakness', 'lack of energy'] },
        { name: 'Dizziness', keywords: ['dizziness', 'dizzy', 'vertigo', 'lightheaded', 'light headed', 'spinning'] },
        { name: 'Back Pain', keywords: ['back pain', 'backache', 'lower back pain', 'back ache', 'spine pain'] },
        { name: 'Joint Pain', keywords: ['joint pain', 'arthralgia', 'joint ache', 'painful joints', 'stiff joints'] },
        { name: 'Skin Rash', keywords: ['rash', 'skin rash', 'red skin', 'itchy skin', 'skin eruption', 'hives'] },
        { name: 'Sore Throat', keywords: ['sore throat', 'throat pain', 'painful throat', 'scratchy throat', 'pharyngitis'] },
        { name: 'Ear Pain', keywords: ['ear pain', 'earache', 'ear ache', 'otalgia', 'pain in ear'] },
        { name: 'Eye Irritation', keywords: ['eye pain', 'eye irritation', 'red eyes', 'itchy eyes', 'watery eyes', 'conjunctivitis'] },
        { name: 'Diarrhea', keywords: ['diarrhea', 'loose stools', 'watery stool', 'frequent bowel'] },
        { name: 'Constipation', keywords: ['constipation', 'difficulty passing stool', 'hard stool', 'infrequent bowel'] },
        { name: 'Vomiting', keywords: ['vomiting', 'throwing up', 'being sick', 'emesis', 'puking'] },
        { name: 'Loss of Appetite', keywords: ['loss of appetite', 'no appetite', 'not hungry', 'decreased appetite'] },
        { name: 'Weight Loss', keywords: ['weight loss', 'losing weight', 'unintentional weight loss'] },
        { name: 'Insomnia', keywords: ['insomnia', 'cannot sleep', 'trouble sleeping', 'sleepless', 'no sleep'] },
        { name: 'Anxiety', keywords: ['anxiety', 'anxious', 'nervous', 'worry', 'stress', 'panic'] },
        { name: 'Depression', keywords: ['depression', 'sad', 'feeling down', 'low mood', 'melancholy'] },
        // Body-specific symptoms
        { name: 'Muscle Pain', keywords: ['muscle pain', 'muscle ache', 'myalgia', 'sore muscles', 'body ache'] },
        { name: 'Neck Pain', keywords: ['neck pain', 'stiff neck', 'neck ache', 'painful neck'] },
        { name: 'Knee Pain', keywords: ['knee pain', 'painful knee', 'knee ache', 'swollen knee'] },
        { name: 'Hand Tremors', keywords: ['tremor', 'shaking', 'trembling', 'hand tremor', 'shaky hands'] },
        { name: 'Swelling', keywords: ['swelling', 'swollen', 'edema', 'puffiness', 'inflamed'] },
        { name: 'High Blood Pressure', keywords: ['high blood pressure', 'hypertension', 'elevated bp', 'blood pressure'] },
        { name: 'Low Blood Sugar', keywords: ['low blood sugar', 'hypoglycemia', 'sugar low', 'shakiness'] },
        { name: 'Allergies', keywords: ['allergies', 'allergy', 'allergic reaction', 'sneezing', 'sneeze'] },
        { name: 'Indigestion', keywords: ['indigestion', 'acid reflux', 'heartburn', 'gas', 'bloating'] },
        { name: 'Menstrual Cramps', keywords: ['menstrual cramps', 'period pain', 'dysmenorrhea', 'cramps'] }
    ];

    // Translations
    const translations = {
        en: {
            analyzing: 'Analyzing your symptoms...',
            pleaseDescribe: 'Please describe your symptoms',
            error: 'Error: ',
            sorryError: 'Sorry, something went wrong. Please try again.'
        },
        hi: {
            analyzing: 'आपके लक्षणों का विश्लेषण हो रहा है...',
            pleaseDescribe: 'कृपया अपने लक्षणों का वर्णन करें',
            error: 'त्रुटि: ',
            sorryError: 'क्षमा करें, कुछ गलत हो गया। कृपया पुनः प्रयास करें।'
        }
    };

    function t(key) {
        const lang = currentLanguage === 'hinglish' ? 'en' : currentLanguage;
        return translations[lang]?.[key] || translations.en[key] || key;
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        // Apply saved theme
        applySavedTheme();
        
        // Check URL for language parameter and set it
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        if (urlLang && ['en', 'hi', 'hinglish'].includes(urlLang)) {
            currentLanguage = urlLang;
            selectedLanguage = urlLang;
            // Auto-select the language button
            setTimeout(() => {
                const btn = document.querySelector(`.lang-btn[data-lang="${urlLang}"]`);
                if (btn) {
                    btn.classList.add('selected');
                }
            }, 100);
        }
        
        // Check if welcome page exists
        const welcomePage = document.getElementById('welcomePage');
        const mainPage = document.getElementById('mainPage');
        
        if (welcomePage && mainPage) {
            initWelcomePage();
        }
    }

    function initWelcomePage() {
        // Device detection
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const deviceIcon = document.getElementById('deviceIcon');
        const deviceText = document.getElementById('deviceText');
        
        if (deviceIcon && deviceText) {
            deviceIcon.textContent = isMobile ? '📱' : '💻';
            deviceText.textContent = isMobile ? 'Mobile Detected' : 'Desktop Detected';
        }
    }

    // Global function for language selection
    window.selectLanguage = function(lang) {
        selectedLanguage = lang;
        currentLanguage = lang;
        
        const langButtons = document.querySelectorAll('.lang-btn');
        langButtons.forEach(btn => {
            if (btn.getAttribute('data-lang') === lang) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });
    };

    // Global function to go to main checker
    window.goToChecker = function() {
        const welcomePage = document.getElementById('welcomePage');
        const mainPage = document.getElementById('mainPage');
        
        if (!welcomePage || !mainPage) return;
        
        // Hide welcome, show main
        welcomePage.style.display = 'none';
        mainPage.style.display = 'block';
        
        // Setup form submission
        setupForm();
    };

    // Global function to go to voice assistant
    window.goToVoiceAssistant = function() {
        window.location.href = '/voice-assistant';
    };

    // Global function to show symptom history
    window.showSymptomHistory = function() {
        const history = JSON.parse(localStorage.getItem('symptomHistory') || '[]');
        
        if (history.length === 0) {
            alert('📋 No symptom history yet!\n\nWhen you analyze symptoms, they will be saved here for your reference.');
            return;
        }
        
        let historyText = '📋 Your Symptom History:\n\n';
        history.slice(0, 10).forEach((item, index) => {
            const date = new Date(item.date).toLocaleDateString();
            historyText += (index + 1) + '. ' + date + '\n';
            historyText += '   Symptoms: ' + item.symptoms.substring(0, 50) + '...\n';
            if (item.condition) {
                historyText += '   Result: ' + item.condition + '\n';
            }
            historyText += '\n';
        });
        
        alert(historyText);
    };

    // Global function to show health tips
    window.showHealthTips = function() {
        const healthTips = [
            { icon: '💧', title: 'Stay Hydrated', tip: 'Drink at least 8 glasses of water daily. Proper hydration helps maintain energy levels and supports overall health.' },
            { icon: '🏃', title: 'Regular Exercise', tip: 'Aim for 30 minutes of moderate exercise daily. Walking, jogging, or yoga can significantly improve your health.' },
            { icon: '🥗', title: 'Balanced Diet', tip: 'Include fruits, vegetables, and whole grains in your diet. Avoid excessive sugar and processed foods.' },
            { icon: '😴', title: 'Quality Sleep', tip: 'Get 7-9 hours of sleep each night. Good sleep is essential for physical and mental well-being.' },
            { icon: '🧘', title: 'Stress Management', tip: 'Practice deep breathing, meditation, or yoga to manage stress. Chronic stress can impact your health negatively.' },
            { icon: '☀️', title: 'Vitamin D', tip: 'Get some sunlight exposure daily. Vitamin D is crucial for bone health and immune function.' },
            { icon: '🚶', title: 'Posture', tip: 'Maintain good posture while sitting and standing. Poor posture can lead to back pain and other issues.' },
            { icon: '🚭', title: 'Avoid Smoking', tip: 'If you smoke, consider quitting. Smoking is a leading cause of many serious health conditions.' }
        ];
        
        let tipsText = '💡 Daily Health Tips:\n\n';
        healthTips.forEach((item, index) => {
            tipsText += (index + 1) + '. ' + item.icon + ' ' + item.title + '\n';
            tipsText += '   ' + item.tip + '\n\n';
        });
        
        alert(tipsText);
    };

    // Global function to show medication reminder
    window.showMedicationReminder = function() {
        const medications = JSON.parse(localStorage.getItem('medications') || '[]');
        
        if (medications.length === 0) {
            // Show default medication reminder info
            const reminderInfo = '💊 Medication Reminder System\n\n' +
                'This feature helps you track your medications.\n\n' +
                'Current Status: No medications saved\n\n' +
                'To add a medication, use voice command:\n' +
                '"Remind me to take [medicine name] at [time]"\n\n' +
                'Example: "Remind me to take aspirin at 8am"';
            alert(reminderInfo);
            return;
        }
        
        let medText = '💊 Your Medications:\n\n';
        medications.forEach((med, index) => {
            medText += (index + 1) + '. ' + med.name + '\n';
            medText += '   Time: ' + med.time + '\n';
            if (med.dosage) {
                medText += '   Dosage: ' + med.dosage + '\n';
            }
            medText += '\n';
        });
        
        alert(medText);
    };

    // Global function to toggle theme
    window.toggleTheme = function() {
        const html = document.documentElement;
        const themeToggle = document.getElementById('themeToggle');
        const isDark = html.getAttribute('data-theme') === 'dark';
        
        if (isDark) {
            html.setAttribute('data-theme', 'light');
            if (themeToggle) themeToggle.textContent = '🌙';
            localStorage.setItem('theme', 'light');
        } else {
            html.setAttribute('data-theme', 'dark');
            if (themeToggle) themeToggle.textContent = '☀️';
            localStorage.setItem('theme', 'dark');
        }
    };
    
    // Global function to go to welcome page
    window.goToWelcome = function() {
        const welcomePage = document.getElementById('welcomePage');
        const mainPage = document.getElementById('mainPage');
        
        if (welcomePage) welcomePage.style.display = 'flex';
        if (mainPage) mainPage.style.display = 'none';
    };
    
    // Global function to toggle language
    window.toggleLanguage = function() {
        const langs = ['en', 'hi', 'hinglish'];
        const currentLang = localStorage.getItem('language') || 'en';
        const currentIndex = langs.indexOf(currentLang);
        const nextIndex = (currentIndex + 1) % langs.length;
        const newLang = langs[nextIndex];
        
        selectLanguage(newLang);
    };
    
    // Global function to select language
    window.selectLanguage = function(lang) {
        currentLanguage = lang;
        selectedLanguage = lang;
        localStorage.setItem('language', lang);
        
        // Update language display
        const langDisplay = document.getElementById('currentLang');
        if (langDisplay) {
            langDisplay.textContent = lang.toUpperCase();
        }
        
        // Update selected button
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.remove('selected');
            if (btn.dataset.lang === lang) {
                btn.classList.add('selected');
            }
        });
    };

    // Global function to check and apply saved theme
    window.applySavedTheme = function() {
        const savedTheme = localStorage.getItem('theme');
        const html = document.documentElement;
        const themeToggle = document.getElementById('themeToggle');
        
        if (savedTheme === 'dark') {
            html.setAttribute('data-theme', 'dark');
            if (themeToggle) themeToggle.textContent = '☀️';
        } else if (savedTheme === 'light') {
            html.setAttribute('data-theme', 'light');
            if (themeToggle) themeToggle.textContent = '🌙';
        }
    };

    // Function to save symptom to history
    function saveToHistory(symptoms, result) {
        const history = JSON.parse(localStorage.getItem('symptomHistory') || '[]');
        history.unshift({
            date: new Date().toISOString(),
            symptoms: symptoms,
            condition: result.matched_condition || result.severity,
            severity: result.severity
        });
        // Keep only last 20 entries
        if (history.length > 20) {
            history.pop();
        }
        localStorage.setItem('symptomHistory', JSON.stringify(history));
    };

    // Global function to set example symptoms in input
    window.setExample = function(symptoms) {
        const symptomsInput = document.getElementById('symptoms');
        if (symptomsInput) {
            symptomsInput.value = symptoms;
            // Focus on the input
            symptomsInput.focus();
            // Optionally scroll to the input
            symptomsInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    };
    
    // Global function to toggle voice recognition
    window.toggleVoiceRecognition = function() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            alert('Voice recognition is not supported in your browser. Please use Chrome or Edge.');
            return;
        }
        
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = currentLanguage === 'hi' ? 'hi-IN' : currentLanguage === 'hinglish' ? 'en-IN' : 'en-US';
        
        const symptomsInput = document.getElementById('symptoms');
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            if (symptomsInput) {
                symptomsInput.value = transcript;
            }
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            alert('Voice recognition error: ' + event.error);
        };
        
        recognition.start();
    };

    // Global function to speak results using browser TTS
    window.speakResults = function() {
        // Get all result text
        const severity = document.getElementById('severityBadge');
        const causesList = document.getElementById('causesList');
        const precautionsList = document.getElementById('precautionsList');
        const emergencyText = document.getElementById('emergencyText');
        
        let textToSpeak = '';
        
        // Debug: check if elements exist
        console.log('speakResults called');
        console.log('severity:', severity);
        console.log('causesList:', causesList);
        
        if (!severity && !causesList && !precautionsList) {
            alert('No results to speak. Please analyze symptoms first.');
            return;
        }
        
        // Get current language
        const lang = currentLanguage || 'en';
        
        // Build text based on language
        if (lang === 'hi') {
            // Pure Hindi
            textToSpeak += 'नमस्कार! ';
            if (severity) textToSpeak += 'गंभीरता स्तर: ' + severity.textContent + '. ';
            if (causesList) {
                const causes = causesList.querySelectorAll('li');
                if (causes.length > 0) {
                    textToSpeak += 'संभावित कारण: ';
                    causes.forEach((cause, i) => {
                        textToSpeak += (i + 1) + '. ' + cause.textContent + '. ';
                    });
                }
            }
            if (precautionsList) {
                const precautions = precautionsList.querySelectorAll('li');
                if (precautions.length > 0) {
                    textToSpeak += 'सावधानियां: ';
                    precautions.forEach((prec, i) => {
                        textToSpeak += (i + 1) + '. ' + prec.textContent + '. ';
                    });
                }
            }
            if (emergencyText && emergencyText.textContent) {
                textToSpeak += 'आपातकालीन चेतावनी: ' + emergencyText.textContent;
            }
        } else if (lang === 'hinglish') {
            // Hinglish - Hindi in Roman script (English letters)
            textToSpeak += 'Namaste! ';
            if (severity) textToSpeak += 'Gambhirta star: ' + severity.textContent + '. ';
            if (causesList) {
                const causes = causesList.querySelectorAll('li');
                if (causes.length > 0) {
                    textToSpeak += 'Sambhavit karan: ';
                    causes.forEach((cause, i) => {
                        textToSpeak += (i + 1) + '. ' + cause.textContent + '. ';
                    });
                }
            }
            if (precautionsList) {
                const precautions = precautionsList.querySelectorAll('li');
                if (precautions.length > 0) {
                    textToSpeak += 'Savdhaniyan: ';
                    precautions.forEach((prec, i) => {
                        textToSpeak += (i + 1) + '. ' + prec.textContent + '. ';
                    });
                }
            }
            if (emergencyText && emergencyText.textContent) {
                textToSpeak += 'Aapatkali chetawani: ' + emergencyText.textContent;
            }
        } else {
            // English
            textToSpeak += 'Hello! ';
            if (severity) textToSpeak += 'Severity level: ' + severity.textContent + '. ';
            if (causesList) {
                const causes = causesList.querySelectorAll('li');
                if (causes.length > 0) {
                    textToSpeak += 'Possible causes: ';
                    causes.forEach((cause, i) => {
                        textToSpeak += (i + 1) + '. ' + cause.textContent + '. ';
                    });
                }
            }
            if (precautionsList) {
                const precautions = precautionsList.querySelectorAll('li');
                if (precautions.length > 0) {
                    textToSpeak += 'Precautions: ';
                    precautions.forEach((prec, i) => {
                        textToSpeak += (i + 1) + '. ' + prec.textContent + '. ';
                    });
                }
            }
            if (emergencyText && emergencyText.textContent) {
                textToSpeak += 'Emergency warning: ' + emergencyText.textContent;
            }
        }
        
        // Use browser's speech synthesis with female voice
        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();
            
            // Get available voices and try to find a female voice
            const voices = window.speechSynthesis.getVoices();
            let selectedVoice = null;
            
            // Try to find a female voice
            const femaleVoiceNames = ['Google हिन्दी', 'Google English', 'Microsoft Zira', 'Samantha', 'Victoria', 'English United Kingdom', 'Google US English'];
            
            for (let voiceName of femaleVoiceNames) {
                selectedVoice = voices.find(v => v.name.includes(voiceName.split(' ')[0]));
                if (selectedVoice) break;
            }
            
            // If no female voice found, use default
            const utterance = new SpeechSynthesisUtterance(textToSpeak);
            // Use Hindi voice for both Hindi and Hinglish (Hinglish uses Roman script Hindi)
            utterance.lang = (lang === 'hi' || lang === 'hinglish') ? 'hi-IN' : 'en-US';
            utterance.rate = 0.9;
            utterance.pitch = 1.2; // Higher pitch for female-sounding voice
            
            if (selectedVoice) {
                utterance.voice = selectedVoice;
            }
            
            window.speechSynthesis.speak(utterance);
        } else {
            alert('Text-to-speech is not supported in your browser.');
        }
    };

    function setupForm() {
        const form = document.getElementById('symptomForm');
        const symptomsInput = document.getElementById('symptoms');
        
        if (form) {
            form.addEventListener('submit', handleSubmit);
        }
        
        // Setup auto-suggest for symptoms input
        if (symptomsInput) {
            symptomsInput.addEventListener('input', debounce(handleInputChange, 300));
            symptomsInput.addEventListener('focus', handleInputChange);
        }
    }

    // Debounce function for input
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Handle input change for auto-suggest
    async function handleInputChange(event) {
        const input = event.target;
        const value = input.value.trim();
        const suggestionsContainer = document.getElementById('suggestionsContainer');
        
        if (!value || value.length < 1) {
            if (suggestionsContainer) {
                suggestionsContainer.innerHTML = '';
                suggestionsContainer.style.display = 'none';
            }
            return;
        }
        
        try {
            // Fetch all conditions
            const response = await fetch('/api/conditions');
            const conditions = await response.json();
            
            // Filter conditions based on input
            const valueLower = value.toLowerCase();
            let suggestions = [];
            
            conditions.forEach(condition => {
                // Check if any keyword matches the input
                condition.keywords.forEach(keyword => {
                    if (keyword.toLowerCase().includes(valueLower)) {
                        suggestions.push({
                            keyword: keyword,
                            name: condition.name
                        });
                    }
                });
            });
            
            // Remove duplicates
            suggestions = [...new Map(suggestions.map(item => [item.keyword, item])).values()];
            
            // Limit to 8 suggestions
            suggestions = suggestions.slice(0, 8);
            
            // Display suggestions
            if (suggestions.length > 0 && suggestionsContainer) {
                suggestionsContainer.innerHTML = suggestions.map(s => 
                    `<div class="suggestion-item" onclick="selectSuggestion('${s.keyword.replace(/'/g, "\\'")}')">${s.keyword}</div>`
                ).join('');
                suggestionsContainer.style.display = 'block';
            } else if (suggestionsContainer) {
                suggestionsContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }

    // Select a suggestion
    window.selectSuggestion = function(value) {
        const symptomsInput = document.getElementById('symptoms');
        const suggestionsContainer = document.getElementById('suggestionsContainer');
        
        if (symptomsInput) {
            // Append to existing text or replace
            if (symptomsInput.value.trim()) {
                symptomsInput.value += ', ' + value;
            } else {
                symptomsInput.value = value;
            }
            symptomsInput.focus();
        }
        
        if (suggestionsContainer) {
            suggestionsContainer.innerHTML = '';
            suggestionsContainer.style.display = 'none';
        }
    };

    async function handleSubmit(event) {
        event.preventDefault();
        
        const symptomsInput = document.getElementById('symptoms');
        const submitBtn = document.getElementById('submitBtn');
        const loadingContainer = document.getElementById('loadingContainer');
        
        if (!symptomsInput) {
            console.error('Symptoms input not found');
            return;
        }

        const symptoms = symptomsInput.value.trim();
        
        if (!symptoms || symptoms.length < 2) {
            showError(t('pleaseDescribe'));
            return;
        }

        // Show loading
        if (submitBtn) submitBtn.disabled = true;
        if (loadingContainer) loadingContainer.classList.add('active');
        
        hideError();
        hideResults();

        try {
            // Call API - include current language
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    symptoms,
                    language: currentLanguage
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to analyze');
            }

            // Display results
            displayResults(data);
            
            // Save to history
            saveToHistory(symptoms, data);
            
        } catch (error) {
            console.error('Error:', error);
            showError(error.message || t('sorryError'));
        } finally {
            // Hide loading
            if (submitBtn) submitBtn.disabled = false;
            if (loadingContainer) loadingContainer.classList.remove('active');
        }
    }

    function displayResults(data) {
        console.log('Displaying results:', data);
        
        // Get all elements fresh
        const resultsSection = document.getElementById('resultsSection');
        const causesList = document.getElementById('causesList');
        const precautionsList = document.getElementById('precautionsList');
        const severityBadge = document.getElementById('severityBadge');
        const severityText = document.getElementById('severityText');
        const emergencyCard = document.getElementById('emergencyCard');
        const emergencyText = document.getElementById('emergencyText');
        
        // Update severity
        if (data.severity && severityBadge) {
            severityBadge.textContent = data.severity;
            severityBadge.className = 'severity-badge ' + data.severity.toLowerCase();
        }
        
        // Update possible causes
        if (data.possible_causes && causesList) {
            causesList.innerHTML = '';
            data.possible_causes.forEach(cause => {
                const li = document.createElement('li');
                li.textContent = cause;
                causesList.appendChild(li);
            });
        }
        
        // Update precautions
        if (data.precautions && precautionsList) {
            precautionsList.innerHTML = '';
            data.precautions.forEach(precaution => {
                const li = document.createElement('li');
                li.textContent = precaution;
                precautionsList.appendChild(li);
            });
        }
        
        // Update emergency warning
        if (data.emergency_warning && emergencyCard && emergencyText) {
            emergencyText.textContent = data.emergency_warning;
            emergencyCard.style.display = 'block';
        } else if (emergencyCard) {
            emergencyCard.style.display = 'none';
        }
        
        // Show results section
        if (resultsSection) {
            resultsSection.classList.add('active');
            resultsSection.style.display = 'flex';
            
            // Scroll to results
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
        
        console.log('Results displayed successfully');
    }

    function showError(message) {
        const errorContainer = document.getElementById('errorContainer');
        const errorText = document.getElementById('errorText');
        
        if (errorText) errorText.textContent = message;
        if (errorContainer) errorContainer.classList.add('active');
    }

    function hideError() {
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) errorContainer.classList.remove('active');
    }

    function hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.classList.remove('active');
            resultsSection.style.display = 'none';
        }
    }

    // Global reset function
    window.resetForm = function() {
        const symptomsInput = document.getElementById('symptoms');
        if (symptomsInput) symptomsInput.value = '';
        
        hideResults();
        hideError();
    };

    // =====================================================
    // EMERGENCY CONTACTS FUNCTIONS
    // =====================================================
    
    window.showEmergencyContacts = async function() {
        const modal = document.getElementById('emergencyModal');
        if (modal) {
            modal.style.display = 'block';
            loadEmergencyContacts('india');
        }
    };
    
    window.closeEmergencyModal = function() {
        const modal = document.getElementById('emergencyModal');
        if (modal) {
            modal.style.display = 'none';
        }
    };
    
    window.closeSpecialistModal = function() {
        const modal = document.getElementById('specialistModal');
        if (modal) {
            modal.style.display = 'none';
        }
    };
    
    window.changeCountry = function() {
        const country = document.getElementById('countrySelector')?.value || 'india';
        loadEmergencyContacts(country);
    };
    
    async function loadEmergencyContacts(country) {
        const grid = document.getElementById('emergencyGrid');
        if (!grid) return;
        
        grid.innerHTML = '<div class="loading">Loading emergency contacts...</div>';
        
        try {
            const response = await fetch(`/api/emergency-contacts?country=${country}`);
            const data = await response.json();
            
            if (data.contacts) {
                displayEmergencyContacts(data.contacts);
            }
        } catch (error) {
            console.error('Error loading emergency contacts:', error);
            grid.innerHTML = '<div class="error">Failed to load contacts. Please try again.</div>';
        }
    }
    
    function displayEmergencyContacts(contacts) {
        const grid = document.getElementById('emergencyGrid');
        if (!grid) return;
        
        const contactsArray = Object.entries(contacts);
        
        grid.innerHTML = contactsArray.map(([key, contact]) => `
            <div class="emergency-contact-card" onclick="callNumber('${contact.number}')">
                <span class="contact-icon">${contact.icon}</span>
                <div class="contact-details">
                    <span class="contact-name">${contact.name}</span>
                    <span class="contact-description">${contact.description || ''}</span>
                </div>
                <span class="contact-number">${contact.number}</span>
            </div>
        `).join('');
    }
    
    window.callNumber = function(number) {
        window.location.href = `tel:${number}`;
    };

    // =====================================================
    // FIND DOCTORS FUNCTIONS
    // =====================================================
    
    let doctorsMap = null;
    let userMarker = null;
    let doctorMarkers = [];
    
    window.showDoctorDirectory = async function() {
        const modal = document.getElementById('doctorsModal');
        if (modal) {
            modal.style.display = 'block';
            await findNearbyDoctors();
        }
    };
    
    window.closeDoctorsModal = function() {
        const modal = document.getElementById('doctorsModal');
        if (modal) {
            modal.style.display = 'none';
        }
    };
    
    async function findNearbyDoctors() {
        const locationStatus = document.getElementById('locationStatus');
        const doctorsList = document.getElementById('doctorsList');
        const specialistInfo = document.getElementById('symptomSpecialistInfo');
        
        // Get symptoms from input
        const symptomsInput = document.getElementById('symptoms');
        const symptoms = symptomsInput?.value || '';
        
        // Update specialist info based on symptoms
        updateSpecialistInfo(symptoms);
        
        if (locationStatus) {
            locationStatus.innerHTML = '<p>📍 Getting your location...</p>';
        }
        
        if (doctorsList) {
            doctorsList.innerHTML = '<div class="loading">Searching for doctors near you...</div>';
        }
        
        // Check if geolocation is available
        if (!navigator.geolocation) {
            if (locationStatus) {
                locationStatus.innerHTML = '<p class="error">❌ Geolocation is not supported by your browser</p>';
            }
            return;
        }
        
        // Get user's location
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const { latitude, longitude } = position.coords;
                
                if (locationStatus) {
                    locationStatus.innerHTML = `<p>✅ Location found! Searching within 10km radius</p>`;
                }
                
                // Initialize map
                initializeMap(latitude, longitude);
                
                // Fetch doctors from API
                await fetchDoctors(latitude, longitude, symptoms);
            },
            (error) => {
                console.error('Geolocation error:', error);
                if (locationStatus) {
                    locationStatus.innerHTML = `<p class="error">❌ Unable to get location: ${error.message}</p>`;
                }
                // Try with default location (Delhi, India)
                const defaultLat = 28.6139;
                const defaultLng = 77.2090;
                initializeMap(defaultLat, defaultLng);
                fetchDoctors(defaultLat, defaultLng, symptoms); // Fixed: removed await
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    }
    
    function updateSpecialistInfo(symptoms) {
        const specialistInfo = document.getElementById('symptomSpecialistInfo');
        const specialistType = document.getElementById('specialistType');
        
        // Analyze symptoms to get specialist type
        fetch('/api/analyze-symptoms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symptoms: symptoms, language: currentLanguage })
        })
        .then(res => res.json())
        .then(data => {
            if (data.specialist) {
                if (specialistInfo) {
                    specialistInfo.innerHTML = `
                        <div class="specialist-recommendation">
                            <span class="specialist-icon">${data.specialist.icon}</span>
                            <div class="specialist-text">
                                <strong>Recommended: ${data.specialist.name}</strong>
                                ${data.is_emergency ? '<span class="emergency-badge">⚠️ Emergency</span>' : ''}
                            </div>
                        </div>
                    `;
                }
                if (specialistType) {
                    specialistType.textContent = data.specialist.name + 's';
                }
            }
        })
        .catch(err => console.error('Error analyzing symptoms:', err));
    }
    
    async function fetchDoctors(lat, lng, symptoms) {
        const doctorsList = document.getElementById('doctorsList');
        
        try {
            const response = await fetch('/api/find-doctors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symptoms: symptoms,
                    latitude: lat,
                    longitude: lng,
                    radius: 10000
                })
            });
            
            const data = await response.json();
            
            if (data.doctors) {
                displayDoctors(data.doctors, lat, lng);
                addDoctorMarkers(data.doctors);
            } else {
                if (doctorsList) {
                    doctorsList.innerHTML = '<div class="error">No doctors found in your area</div>';
                }
            }
        } catch (error) {
            console.error('Error fetching doctors:', error);
            if (doctorsList) {
                doctorsList.innerHTML = '<div class="error">Failed to load doctors. Please try again.</div>';
            }
        }
    }
    
    function displayDoctors(doctors, userLat, userLng) {
        const doctorsList = document.getElementById('doctorsList');
        if (!doctorsList) return;
        
        if (doctors.length === 0) {
            doctorsList.innerHTML = '<div class="no-results">No doctors found nearby</div>';
            return;
        }
        
        doctorsList.innerHTML = doctors.map(doctor => `
            <div class="doctor-card">
                <div class="doctor-header">
                    <span class="doctor-icon">${doctor.icon || '🩺'}</span>
                    <div class="doctor-info">
                        <h4>${doctor.name}</h4>
                        <span class="doctor-specialization">${doctor.specialization || 'General Physician'}</span>
                    </div>
                </div>
                <div class="doctor-details">
                    <p class="doctor-address">📍 ${doctor.address}</p>
                    ${doctor.distance_km ? `<p class="doctor-distance">🚗 ${doctor.distance_km} km away</p>` : ''}
                    ${doctor.rating ? `<p class="doctor-rating">⭐ ${doctor.rating} (${doctor.user_ratings_total || 0} reviews)</p>` : ''}
                    ${doctor.open_now !== undefined ? `<p class="doctor-status">${doctor.open_now ? '🟢 Open Now' : doctor.open_now === false ? '🔴 Closed' : '⚪ Hours Unknown'}</p>` : ''}
                </div>
                <div class="doctor-actions">
                    ${doctor.phone ? `<button class="doctor-btn call-btn" onclick="callDoctor('${doctor.phone}')">📞 Call</button>` : ''}
                    <button class="doctor-btn directions-btn" onclick="getDirections(${userLat}, ${userLng}, ${doctor.location.lat}, ${doctor.location.lng})">🧭 Directions</button>
                </div>
            </div>
        `).join('');
    }
    
    function initializeMap(lat, lng) {
        const mapContainer = document.getElementById('mapContainer');
        const mapDiv = document.getElementById('doctorsMap');
        
        if (mapContainer && mapDiv) {
            mapContainer.style.display = 'block';
            
            // Check if Google Maps is loaded
            if (typeof google !== 'undefined' && google.maps) {
                const mapOptions = {
                    center: { lat: lat, lng: lng },
                    zoom: 13,
                    mapTypeControl: false,
                    streetViewControl: false
                };
                
                doctorsMap = new google.maps.Map(mapDiv, mapOptions);
                
                // Add user marker
                userMarker = new google.maps.Marker({
                    position: { lat: lat, lng: lng },
                    map: doctorsMap,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 10,
                        fillColor: '#4285F4',
                        fillOpacity: 1,
                        strokeColor: '#ffffff',
                        strokeWeight: 2
                    },
                    title: 'Your Location'
                });
            } else {
                mapDiv.innerHTML = '<div class="map-placeholder">📍 Map View (Enable Google Maps API for interactive map)</div>';
            }
        }
    }
    
    function addDoctorMarkers(doctors) {
        if (!doctorsMap || typeof google === 'undefined') return;
        
        // Clear existing markers
        doctorMarkers.forEach(marker => marker.setMap(null));
        doctorMarkers = [];
        
        doctors.forEach(doctor => {
            const marker = new google.maps.Marker({
                position: { lat: doctor.location.lat, lng: doctor.location.lng },
                map: doctorsMap,
                title: doctor.name
            });
            
            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div class="map-info-window">
                        <strong>${doctor.name}</strong><br>
                        ${doctor.specialization || ''}<br>
                        ${doctor.rating ? `⭐ ${doctor.rating}` : ''}
                    </div>
                `
            });
            
            marker.addListener('click', () => {
                infoWindow.open(doctorsMap, marker);
            });
            
            doctorMarkers.push(marker);
        });
    }
    
    window.callDoctor = function(phone) {
        window.location.href = `tel:${phone}`;
    };
    
    window.getDirections = function(originLat, originLng, destLat, destLng) {
        const url = `https://www.google.com/maps/dir/${originLat},${originLng}/${destLat},${destLng}`;
        window.open(url, '_blank');
    };

    // =====================================================
    // SYMPTOM HISTORY, HEALTH TIPS, MEDICATION REMINDER
    // (Placeholder functions for quick action buttons)
    // =====================================================
    
    // CLICK OUTSIDE TO CLOSE MODALS
    // =====================================================
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });

})();
