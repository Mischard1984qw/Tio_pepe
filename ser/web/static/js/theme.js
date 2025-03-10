document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    themeToggle.setAttribute('aria-label', 'Toggle dark mode');
    document.body.appendChild(themeToggle);

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'dark') {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }

    // Theme toggle handler
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        themeToggle.innerHTML = newTheme === 'dark' ? 
            '<i class="fas fa-sun"></i>' : 
            '<i class="fas fa-moon"></i>';
    });

    // Interactive Tutorial
    class Tutorial {
        constructor() {
            this.steps = [
                {
                    target: '.nav-menu',
                    content: 'Use the navigation menu to access different sections of the system.',
                    position: 'bottom'
                },
                {
                    target: '.dashboard-grid',
                    content: 'This is your customizable dashboard. Drag and drop widgets to rearrange them.',
                    position: 'top'
                },
                {
                    target: '.theme-toggle',
                    content: 'Toggle between light and dark mode for better visibility.',
                    position: 'left'
                }
            ];
            this.currentStep = 0;
            this.overlay = null;
            this.stepElement = null;
        }

        start() {
            if (!localStorage.getItem('tutorial_completed')) {
                this.createOverlay();
                this.showStep();
            }
        }

        createOverlay() {
            this.overlay = document.createElement('div');
            this.overlay.className = 'tutorial-overlay';
            document.body.appendChild(this.overlay);

            this.stepElement = document.createElement('div');
            this.stepElement.className = 'tutorial-step';
            this.overlay.appendChild(this.stepElement);
        }

        showStep() {
            const step = this.steps[this.currentStep];
            const target = document.querySelector(step.target);
            
            if (!target) {
                this.end();
                return;
            }

            const targetRect = target.getBoundingClientRect();
            this.overlay.classList.add('active');
            
            this.stepElement.innerHTML = `
                <div class="tutorial-content">${step.content}</div>
                <div class="btn-group">
                    ${this.currentStep > 0 ? '<button class="btn-prev">Previous</button>' : ''}
                    <button class="btn-${this.currentStep === this.steps.length - 1 ? 'finish' : 'next'}">
                        ${this.currentStep === this.steps.length - 1 ? 'Finish' : 'Next'}
                    </button>
                </div>
            `;

            // Position the step element
            const stepRect = this.stepElement.getBoundingClientRect();
            let top, left;

            switch(step.position) {
                case 'top':
                    top = targetRect.top - stepRect.height - 10;
                    left = targetRect.left + (targetRect.width - stepRect.width) / 2;
                    break;
                case 'bottom':
                    top = targetRect.bottom + 10;
                    left = targetRect.left + (targetRect.width - stepRect.width) / 2;
                    break;
                case 'left':
                    top = targetRect.top + (targetRect.height - stepRect.height) / 2;
                    left = targetRect.left - stepRect.width - 10;
                    break;
                case 'right':
                    top = targetRect.top + (targetRect.height - stepRect.height) / 2;
                    left = targetRect.right + 10;
                    break;
            }

            this.stepElement.style.top = `${Math.max(10, top)}px`;
            this.stepElement.style.left = `${Math.max(10, left)}px`;

            // Add event listeners
            const btnNext = this.stepElement.querySelector('.btn-next, .btn-finish');
            const btnPrev = this.stepElement.querySelector('.btn-prev');

            if (btnNext) {
                btnNext.addEventListener('click', () => {
                    if (this.currentStep === this.steps.length - 1) {
                        this.end();
                    } else {
                        this.currentStep++;
                        this.showStep();
                    }
                });
            }

            if (btnPrev) {
                btnPrev.addEventListener('click', () => {
                    this.currentStep--;
                    this.showStep();
                });
            }
        }

        end() {
            this.overlay.remove();
            localStorage.setItem('tutorial_completed', 'true');
        }
    }

    // Initialize tutorial
    const tutorial = new Tutorial();
    
    // Start tutorial when clicking the help button
    const helpButton = document.querySelector('.help-button');
    if (helpButton) {
        helpButton.addEventListener('click', () => tutorial.start());
    } else {
        // If no help button exists, start tutorial automatically for new users
        if (!localStorage.getItem('tutorial_completed')) {
            tutorial.start();
        }
    }
});