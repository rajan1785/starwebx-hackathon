const { createApp } = Vue;

const API_BASE_URL = 'http://localhost:8000/api';

const app = createApp({
    data() {
        return {
            currentScreen: 'instructions', // instructions, exam, results
            currentSection: 'mcq', // mcq, programming
            
            // Timer
            totalTimeMinutes: 60,
            timeRemaining: 60 * 60, // seconds
            timerInterval: null,
            
            // MCQ
            mcqQuestions: [],
            currentMCQIndex: 0,
            mcqAnswers: {}, // { questionId: 'A/B/C/D' }
            
            // Programming
            programmingProblems: [],
            currentProblemIndex: 0,
            selectedLanguage: 'python',
            monacoEditor: null,
            programmingSubmissions: {}, // { problemId: { code, language, result } }
            codeResult: null,
            
            // Tab tracking
            tabActivityCount: 0,
            showTabWarning: false,
            isFullscreen: false,
            
            token: null
        };
    },
    computed: {
        currentMCQ() {
            return this.mcqQuestions[this.currentMCQIndex] || null;
        },
        currentProblem() {
            return this.programmingProblems[this.currentProblemIndex] || null;
        }
    },
    methods: {
        async startExam() {
            try {
                // Enter fullscreen
                const elem = document.documentElement;
                if (elem.requestFullscreen) {
                    await elem.requestFullscreen();
                }
                
                this.isFullscreen = true;
                
                // Load questions
                await this.loadMCQQuestions();
                await this.loadProgrammingProblems();
                
                // Start timer
                this.startTimer();
                
                // Switch to exam screen
                this.currentScreen = 'exam';
                
                // Load Monaco editor after screen change
                this.$nextTick(() => {
                    this.initMonacoEditor();
                });
                
            } catch (error) {
                console.error('Failed to start exam:', error);
                alert('Failed to start exam. Please try again.');
            }
        },
        
        async loadMCQQuestions() {
            try {
                const response = await axios.get(`${API_BASE_URL}/stage1/mcq/questions`);
                this.mcqQuestions = response.data;
            } catch (error) {
                console.error('Failed to load MCQ questions:', error);
                alert('Failed to load questions. Please refresh the page.');
            }
        },
        
        async loadProgrammingProblems() {
            try {
                const response = await axios.get(`${API_BASE_URL}/stage1/programming/problems`);
                this.programmingProblems = response.data;
            } catch (error) {
                console.error('Failed to load programming problems:', error);
                alert('Failed to load programming problems. Please refresh the page.');
            }
        },
        
        initMonacoEditor() {
            require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' } });
            
            require(['vs/editor/editor.main'], () => {
                this.monacoEditor = monaco.editor.create(document.getElementById('monaco-editor'), {
                    value: this.getStarterCode(),
                    language: this.getMonacoLanguage(),
                    theme: 'vs-dark',
                    automaticLayout: true,
                    fontSize: 14,
                    minimap: { enabled: false }
                });
            });
        },
        
        getMonacoLanguage() {
            const languageMap = {
                'python': 'python',
                'java': 'java',
                'cpp': 'cpp',
                'javascript': 'javascript'
            };
            return languageMap[this.selectedLanguage] || 'python';
        },
        
        getStarterCode() {
            if (!this.currentProblem) return '';
            
            const starterCodeMap = {
                'python': this.currentProblem.starter_code_python,
                'java': this.currentProblem.starter_code_java,
                'cpp': this.currentProblem.starter_code_cpp,
                'javascript': this.currentProblem.starter_code_javascript
            };
            
            return starterCodeMap[this.selectedLanguage] || '';
        },
        
        loadStarterCode() {
            if (this.monacoEditor) {
                this.monacoEditor.setValue(this.getStarterCode());
                monaco.editor.setModelLanguage(this.monacoEditor.getModel(), this.getMonacoLanguage());
            }
        },
        
        selectMCQOption(questionId, option) {
            this.mcqAnswers[questionId] = option;
        },
        
        async saveAndNextMCQ() {
            if (this.currentMCQ && this.mcqAnswers[this.currentMCQ.id]) {
                await this.submitMCQAnswer(this.currentMCQ.id, this.mcqAnswers[this.currentMCQ.id]);
            }
            this.nextMCQ();
        },
        
        previousMCQ() {
            if (this.currentMCQIndex > 0) {
                this.currentMCQIndex--;
            }
        },
        
        nextMCQ() {
            if (this.currentMCQIndex < this.mcqQuestions.length - 1) {
                this.currentMCQIndex++;
            }
        },
        
        async submitMCQAnswer(questionId, selectedOption) {
            try {
                await axios.post(`${API_BASE_URL}/stage1/mcq/submit`, {
                    question_id: questionId,
                    selected_option: selectedOption,
                    time_taken: null
                });
            } catch (error) {
                console.error('Failed to submit MCQ answer:', error);
            }
        },
        
        runCode() {
            alert('Code preview - AI evaluation happens on submit');
        },
        
        async submitCode() {
            if (!this.monacoEditor) return;
            
            const code = this.monacoEditor.getValue();
            
            if (!code.trim()) {
                alert('Please write some code before submitting.');
                return;
            }
            
            try {
                const response = await axios.post(`${API_BASE_URL}/stage1/programming/submit`, {
                    problem_id: this.currentProblem.id,
                    code: code,
                    language: this.selectedLanguage
                });
                
                this.codeResult = response.data.evaluation;
                this.programmingSubmissions[this.currentProblem.id] = {
                    code: code,
                    language: this.selectedLanguage,
                    result: this.codeResult
                };
                
                alert(`Code submitted! Score: ${this.codeResult.score}/10`);
                
            } catch (error) {
                console.error('Failed to submit code:', error);
                alert('Failed to submit code. Please try again.');
            }
        },
        
        async submitExam() {
            if (!confirm('Are you sure you want to submit the exam? You cannot make changes after submission.')) {
                return;
            }
            
            try {
                await axios.post(`${API_BASE_URL}/stage1/complete`);
                
                // Stop timer
                if (this.timerInterval) {
                    clearInterval(this.timerInterval);
                }
                
                // Exit fullscreen
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
                
                this.currentScreen = 'results';
                
            } catch (error) {
                console.error('Failed to submit exam:', error);
                alert('Failed to submit exam. Please try again.');
            }
        },
        
        startTimer() {
            this.timerInterval = setInterval(() => {
                this.timeRemaining--;
                
                if (this.timeRemaining <= 0) {
                    this.timeRemaining = 0;
                    clearInterval(this.timerInterval);
                    alert('Time is up! Exam will be auto-submitted.');
                    this.submitExam();
                }
            }, 1000);
        },
        
        formatTime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        },
        
        async trackTabSwitch() {
            if (this.currentScreen === 'exam' && this.currentSection === 'programming' && this.currentProblem) {
                try {
                    const response = await axios.post(`${API_BASE_URL}/stage1/programming/track-tab`, null, {
                        params: { problem_id: this.currentProblem.id }
                    });
                    this.tabActivityCount = response.data.tab_activity_count;
                    
                    // Show warning
                    this.showTabWarning = true;
                    setTimeout(() => {
                        this.showTabWarning = false;
                    }, 3000);
                    
                } catch (error) {
                    console.error('Failed to track tab switch:', error);
                }
            }
        },
        
        returnToDashboard() {
            window.location.href = 'index.html';
        },
        
        checkAuth() {
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = 'index.html';
                return;
            }
            
            this.token = token;
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
    },
    mounted() {
        this.checkAuth();
        
        // Track fullscreen changes
        document.addEventListener('fullscreenchange', () => {
            if (!document.fullscreenElement && this.currentScreen === 'exam') {
                this.isFullscreen = false;
                this.trackTabSwitch();
            } else {
                this.isFullscreen = true;
            }
        });
        
        // Track visibility changes (tab switches)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.currentScreen === 'exam') {
                this.trackTabSwitch();
            }
        });
        
        // Prevent right-click during exam
        document.addEventListener('contextmenu', (e) => {
            if (this.currentScreen === 'exam') {
                e.preventDefault();
            }
        });
    },
    beforeUnmount() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
    }
});

app.mount('#app');