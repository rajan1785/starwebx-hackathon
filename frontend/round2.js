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
            screenshots: [], // Array of uploaded filenames
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
                this.projectForm.tech_stack.length > 0 &&
                this.screenshots.length >= 3
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
                    this.screenshots = project.screenshots || [];
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
        
        async handleFileSelect(event) {
            const files = Array.from(event.target.files);
            await this.uploadFiles(files);
        },
        
        async handleDrop(event) {
            this.isDragging = false;
            const files = Array.from(event.dataTransfer.files);
            await this.uploadFiles(files);
        },
        
        async uploadFiles(files) {
            for (const file of files) {
                // Validate file type
                if (!file.type.startsWith('image/')) {
                    showToast(`${file.name} is not an image file`, '#EF4444');
                    continue;
                }
                
                // Validate file size (5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showToast(`${file.name} is too large. Maximum size is 5MB`, '#EF4444');
                    continue;
                }
                
                // Upload file
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await axios.post(
                        `${API_BASE_URL}/stage2/upload-screenshot`,
                        formData,
                        {
                            headers: {
                                'Content-Type': 'multipart/form-data'
                            }
                        }
                    );
                    
                    this.screenshots.push(response.data.filename);
                    
                } catch (error) {
                    console.error('Failed to upload file:', error);
                    showToast(`Failed to upload ${file.name}`, '#EF4444');
                }
            }
        },
        
        async removeScreenshot(index) {
            if (!confirm('Are you sure you want to remove this screenshot?')) {
                return;
            }
            
            const filename = this.screenshots[index];
            
            try {
                await axios.delete(`${API_BASE_URL}/stage2/screenshot/${filename}`);
                this.screenshots.splice(index, 1);
            } catch (error) {
                console.error('Failed to delete screenshot:', error);
                // Remove from UI anyway
                this.screenshots.splice(index, 1);
            }
        },
        
        getScreenshotUrl(filename) {
            return `${API_BASE_URL.replace('/api', '')}/uploads/${filename}`;
        },
        
        async saveProgress() {
            if (!this.projectForm.project_title.trim()) {
                showToast('Please enter a project title', '#EF4444');
                return;
            }
            
            try {
                await axios.put(`${API_BASE_URL}/stage2/update`, this.projectForm, {
                    params: {
                        screenshots: this.screenshots
                    }
                });
                
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
                    submitData,
                    {
                        params: {
                            screenshots: this.screenshots
                        }
                    }
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