const { createApp } = Vue;

const API_BASE_URL = 'http://localhost:8000/api';

const app = createApp({
    data() {
        return {
            loading: true,
            isEligible: false,
            assignment: null,
            submissionStatus: 'not_started',
            projectForm: {
                project_title: '',
                project_description: '',
                github_repo_url: '',
                live_demo_url: '',
                tech_stack: []
            },
            newTech: '',
            isDragging: false,
            token: null
        };
    },
    computed: {
        isSubmitted() {
            return this.submissionStatus === 'submitted';
        },
        canSubmit() {
            return (
                this.projectForm.project_title.trim() !== '' &&
                this.projectForm.project_description.trim() !== '' &&
                this.projectForm.github_repo_url.trim() !== '' &&
                this.projectForm.tech_stack.length > 0
            );
        }
    },
    methods: {
        async loadAssignment() {
            try {
                const response = await axios.get(`${API_BASE_URL}/stage2/assignment`);
                this.assignment = response.data;
                this.isEligible = true;
                
                // Load existing submission if any
                await this.loadExistingSubmission();
                
            } catch (error) {
                console.error('Failed to load assignment:', error);
                if (error.response && error.response.status === 403) {
                    this.isEligible = false;
                } else {
                    showToast('Failed to load assignment. Please try again.', '#EF4444');
                }
            } finally {
                this.loading = false;
            }
        },
        
        async loadExistingSubmission() {
            try {
                const response = await axios.get(`${API_BASE_URL}/stage2/submission`);
                const project = response.data;
                
                if (project) {
                    this.projectForm.project_title = project.project_title || '';
                    this.projectForm.project_description = project.project_description || '';
                    this.projectForm.github_repo_url = project.github_repo_url || '';
                    this.projectForm.live_demo_url = project.live_demo_url || '';
                    this.projectForm.tech_stack = project.tech_stack || [];
                    this.submissionStatus = project.submission_status;
                }
            } catch (error) {
                // No existing submission - that's okay
                console.log('No existing submission found');
            }
        },
        
        addTech() {
            const tech = this.newTech.trim();
            if (tech && !this.projectForm.tech_stack.includes(tech)) {
                this.projectForm.tech_stack.push(tech);
                this.newTech = '';
            }
        },
        
        removeTech(index) {
            this.projectForm.tech_stack.splice(index, 1);
        },
        
        async saveProgress() {
            if (!this.projectForm.project_title.trim()) {
                showToast('Please enter a project title', '#EF4444');
                return;
            }
            
            try {
await axios.put(`${API_BASE_URL}/stage2/update`, this.projectForm);
                
                showToast('Progress saved successfully!', '#4BB543');
                this.submissionStatus = 'in_progress';
                
            } catch (error) {
                console.error('Failed to save progress:', error);
                showToast('Failed to save progress. Please try again.', '#EF4444');
            }
        },
        
        async submitProject() {
            if (!this.canSubmit) {
                showToast('Please fill all required fields and upload at least 3 screenshots', '#EF4444');
                return;
            }
            
            if (!confirm('Are you sure you want to submit? You cannot make changes after submission.')) {
                return;
            }
            
            try {
                const submitData = {
                    ...this.projectForm
                };
                
                const response = await axios.post(
                    `${API_BASE_URL}/stage2/submit`,
                    submitData
                );
                
                this.submissionStatus = 'submitted';
                
                showToast('Project submitted successfully! 🎉\n\nResults will be announced soon.', '#4BB543');
                
            } catch (error) {
                console.error('Failed to submit project:', error);
                showToast('Failed to submit project. Please try again.', '#EF4444');
            }
        },
        
        formatDeadline(deadline) {
            const date = new Date(deadline);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
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
        this.loadAssignment();
    }
});

app.mount('#app');