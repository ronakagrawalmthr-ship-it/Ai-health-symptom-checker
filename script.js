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

    // Global function to show emergency contacts
    window.showEmergencyContacts = function() {
        const emergencyInfo = `
            <div style="text-align: left; padding: 20px;">
                <h3 style="color: #ff4757; margin-bottom: 20px;">🚑 Emergency Contacts (India)</h3>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <strong>🚑 Ambulance</strong><br>
                    <a href="tel:102" style="color: #00d4ff; font-size: 18px;">102</a> - Ambulance<br>
                    <a href="tel:108" style="color: #00d4ff; font-size: 18px;">108</a> - Emergency
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <strong>🏥 National Health Helpline</strong><br>
                    <a href="tel:104" style="color: #00d4ff; font-size: 18px;">104</a> - Health Advisory
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <strong>👨‍⚕️ COVID-19</strong><br>
                    <a href="tel:1075" style="color: #00d4ff; font-size: 18px;">1075</a> - Helpline
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <strong>🚨 Police</strong><br>
                    <a href="tel:100" style="color: #00d4ff; font-size: 18px;">100</a> - Police
                </div>
                
                <p style="color: #ff6b6b; font-size: 14px; margin-top: 20px;">
                    ⚠️ For life-threatening emergencies, call 102 or go to the nearest hospital immediately!
                </p>
            </div>`;
        alert(emergencyInfo);
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
        const tips = '💡 Daily Health Tips:\n\n1. 🥗 Eat a balanced diet with fruits and vegetables\n2. 💧 Drink at least 8 glasses of water daily\n3. 😴 Get 7-8 hours of sleep every night\n4. 🚶 Exercise for at least 30 minutes daily\n5. 🧘 Practice stress management techniques\n6. 🏥 Get regular health check-ups\n7. 💊 Take medications as prescribed\n8. 🚭 Avoid smoking and excessive alcohol\n9. 🧴 Maintain personal hygiene\n10. 😷 Stay updated on vaccinations\n\nRemember: Prevention is better than cure!';
        alert(tips);
    };

    // Global function to show medication reminder
    window.showMedicationReminder = function() {
        const reminderInfo = '💊 Medication Reminder\n\nSet reminders for your medications:\n\n• Morning (8:00 AM) - Breakfast\n• Afternoon (2:00 PM) - Lunch  \n• Evening (6:00 PM) - Dinner\n• Night (10:00 PM) - Before bed\n\n📝 Features:\n• Add custom medications\n• Set frequency (daily, weekly)\n• Get browser notifications\n• Track medication history\n\n⚠️ Note: This is a reminder feature. Always consult your doctor before taking any medications.';
        alert(reminderInfo);
    };

    // Global function to show doctor directory placeholder
    window.showDoctorDirectory = function() {
        const doctorInfo = '👨‍⚕️ Find a Doctor\n\nComing Soon!\n\n🔍 We\'ll help you find:\n• General Physicians\n• Specialists (Cardiologist, Neurologist, etc.)\n• Nearby Hospitals & Clinics\n• Emergency Services\n\n📍 Features:\n• Search by specialty\n• View doctor ratings\n• Get directions\n• Book appointments\n\nFor now, please consult your local doctor for any health concerns.';
        alert(doctorInfo);
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

})();
