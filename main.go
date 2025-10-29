package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Styles
var (
	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#7D56F4")).
			MarginBottom(1)

	subtitleStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#666666")).
			MarginBottom(1)

	focusedStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#7D56F4")).
			Bold(true)

	cursorStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#7D56F4"))

	selectedStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00D787")).
			Bold(true)

	helpStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#626262")).
			MarginTop(1)

	errorStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FF0000")).
			Bold(true)

	successStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00D787")).
			Bold(true)
)

type step int

const (
	stepProjectName step = iota
	stepProjectDescription
	stepAuthor
	stepEmail
	stepPythonVersion
	stepBackendPort
	stepFeatures
	stepConfirm
	stepExecuting
	stepDone
)

type model struct {
	step            step
	textInput       textinput.Model
	cursor          int
	err             error
	executing       bool
	executionOutput string
	executionError  error

	// Collected data
	projectName        string
	projectDescription string
	author             string
	email              string
	pythonVersion      string
	backendPort        string
	useDocker          bool
	usePostgres        bool
	useSupabase        bool
	aiProject          bool
	useCelery          bool
}

type executionCompleteMsg struct {
	output string
	err    error
}

func initialModel() model {
	ti := textinput.New()
	ti.Placeholder = "My Awesome Project"
	ti.Focus()
	ti.CharLimit = 156
	ti.Width = 50

	return model{
		step:          stepProjectName,
		textInput:     ti,
		pythonVersion: "3.14",
		backendPort:   "8000",
		useDocker:     true,
		usePostgres:   true,
		useSupabase:   true,
		aiProject:     true,
		useCelery:     true,
	}
}

func (m model) Init() tea.Cmd {
	return textinput.Blink
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			if m.step == stepDone || m.step == stepExecuting {
				return m, tea.Quit
			}
			return m, tea.Quit

		case "enter":
			return m.handleEnter()

		case "up", "k":
			if m.step == stepFeatures && m.cursor > 0 {
				m.cursor--
			}

		case "down", "j":
			if m.step == stepFeatures && m.cursor < 4 {
				m.cursor++
			}

		case " ", "space":
			if m.step == stepFeatures {
				m.toggleFeature()
			} else if m.step == stepConfirm {
				m.cursor = (m.cursor + 1) % 2
			}

		case "tab":
			if m.step == stepConfirm {
				m.cursor = (m.cursor + 1) % 2
			}
		}

	case executionCompleteMsg:
		m.executing = false
		m.executionOutput = msg.output
		m.executionError = msg.err
		m.step = stepDone
		return m, nil
	}

	// Update text input
	if m.isTextInputStep() {
		m.textInput, cmd = m.textInput.Update(msg)
	}

	return m, cmd
}

func (m *model) handleEnter() (tea.Model, tea.Cmd) {
	switch m.step {
	case stepProjectName:
		if m.textInput.Value() != "" {
			m.projectName = m.textInput.Value()
			m.step = stepProjectDescription
			m.textInput.SetValue("")
			m.textInput.Placeholder = "A modern FastAPI application"
		}

	case stepProjectDescription:
		if m.textInput.Value() != "" {
			m.projectDescription = m.textInput.Value()
			m.step = stepAuthor
			m.textInput.SetValue("")
			m.textInput.Placeholder = "Your Name"
		}

	case stepAuthor:
		if m.textInput.Value() != "" {
			m.author = m.textInput.Value()
			m.step = stepEmail
			m.textInput.SetValue("")
			m.textInput.Placeholder = "your.email@example.com"
		}

	case stepEmail:
		if m.textInput.Value() != "" {
			m.email = m.textInput.Value()
			m.step = stepPythonVersion
			m.textInput.SetValue(m.pythonVersion)
			m.textInput.Placeholder = "3.14"
		}

	case stepPythonVersion:
		if m.textInput.Value() != "" {
			m.pythonVersion = m.textInput.Value()
			m.step = stepBackendPort
			m.textInput.SetValue(m.backendPort)
			m.textInput.Placeholder = "8000"
		}

	case stepBackendPort:
		if m.textInput.Value() != "" {
			m.backendPort = m.textInput.Value()
			m.step = stepFeatures
			m.cursor = 0
		}

	case stepFeatures:
		m.step = stepConfirm
		m.cursor = 0

	case stepConfirm:
		if m.cursor == 0 { // Confirm
			m.step = stepExecuting
			m.executing = true
			return m, m.executeSetup()
		} else { // Go back
			m.step = stepFeatures
			m.cursor = 0
		}

	case stepDone:
		return m, tea.Quit
	}

	return m, nil
}

func (m *model) toggleFeature() {
	switch m.cursor {
	case 0:
		m.useDocker = !m.useDocker
	case 1:
		m.usePostgres = !m.usePostgres
	case 2:
		m.useSupabase = !m.useSupabase
	case 3:
		m.aiProject = !m.aiProject
	case 4:
		m.useCelery = !m.useCelery
	}
}

func (m model) isTextInputStep() bool {
	return m.step >= stepProjectName && m.step <= stepBackendPort
}

func (m model) View() string {
	if m.step == stepExecuting {
		return m.renderExecuting()
	}

	if m.step == stepDone {
		return m.renderDone()
	}

	var s strings.Builder

	// Header
	s.WriteString(titleStyle.Render("🚀 FastAPI Project Generator"))
	s.WriteString("\n")
	s.WriteString(subtitleStyle.Render("Let's create your production-ready FastAPI application"))
	s.WriteString("\n\n")

	// Progress indicator
	progress := fmt.Sprintf("Step %d of 8", int(m.step)+1)
	s.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("#888888")).Render(progress))
	s.WriteString("\n\n")

	// Current step content
	switch m.step {
	case stepProjectName:
		s.WriteString(m.renderTextInput("Project Name", "What should we call your project?"))
	case stepProjectDescription:
		s.WriteString(m.renderTextInput("Project Description", "Briefly describe your project"))
	case stepAuthor:
		s.WriteString(m.renderTextInput("Author Name", "Who's the author of this project?"))
	case stepEmail:
		s.WriteString(m.renderTextInput("Email", "Your email address"))
	case stepPythonVersion:
		s.WriteString(m.renderTextInput("Python Version", "Which Python version? (e.g., 3.14, 3.12)"))
	case stepBackendPort:
		s.WriteString(m.renderTextInput("Backend Port", "Which port should the backend run on?"))
	case stepFeatures:
		s.WriteString(m.renderFeatures())
	case stepConfirm:
		s.WriteString(m.renderConfirmation())
	}

	return s.String()
}

func (m model) renderTextInput(label, subtitle string) string {
	var s strings.Builder
	s.WriteString(focusedStyle.Render(label))
	s.WriteString("\n")
	s.WriteString(subtitleStyle.Render(subtitle))
	s.WriteString("\n\n")
	s.WriteString(m.textInput.View())
	s.WriteString("\n\n")
	s.WriteString(helpStyle.Render("Press Enter to continue • Ctrl+C to quit"))
	return s.String()
}

func (m model) renderFeatures() string {
	var s strings.Builder
	s.WriteString(focusedStyle.Render("Select Features"))
	s.WriteString("\n")
	s.WriteString(subtitleStyle.Render("Choose which features to include in your project"))
	s.WriteString("\n\n")

	features := []struct {
		name        string
		description string
		enabled     bool
	}{
		{"Docker Support", "Containerization with Docker & Docker Compose", m.useDocker},
		{"PostgreSQL", "Production-ready database with SQLAlchemy", m.usePostgres},
		{"Supabase", "Backend-as-a-Service integration", m.useSupabase},
		{"AI Project", "LangGraph agent with tool calling", m.aiProject},
		{"Celery Workers", "Distributed task queue for background jobs", m.useCelery},
	}

	for i, feature := range features {
		cursor := "  "
		if m.cursor == i {
			cursor = cursorStyle.Render("▸ ")
		}

		checkbox := "[ ]"
		if feature.enabled {
			checkbox = selectedStyle.Render("[ ✓ ]")
		}

		line := fmt.Sprintf("%s%s %s", cursor, checkbox, feature.name)
		if m.cursor == i {
			line = focusedStyle.Render(line)
		}
		s.WriteString(line)
		s.WriteString("\n")
		s.WriteString("    " + lipgloss.NewStyle().Foreground(lipgloss.Color("#888888")).Render(feature.description))
		s.WriteString("\n")
	}

	s.WriteString("\n")
	s.WriteString(helpStyle.Render("↑/↓: Navigate • Space: Toggle • Enter: Continue • Ctrl+C: Quit"))
	return s.String()
}

func (m model) renderConfirmation() string {
	var s strings.Builder
	s.WriteString(focusedStyle.Render("📋 Confirm Configuration"))
	s.WriteString("\n")
	s.WriteString(subtitleStyle.Render("Please review your project configuration"))
	s.WriteString("\n\n")

	projectSlug := strings.ToLower(strings.ReplaceAll(m.projectName, " ", "-"))

	configs := []struct{ key, value string }{
		{"Project Name", m.projectName},
		{"Project Slug", projectSlug},
		{"Description", m.projectDescription},
		{"Author", m.author},
		{"Email", m.email},
		{"Python Version", m.pythonVersion},
		{"Backend Port", m.backendPort},
		{"Docker", yesNo(m.useDocker)},
		{"PostgreSQL", yesNo(m.usePostgres)},
		{"Supabase", yesNo(m.useSupabase)},
		{"AI Project", yesNo(m.aiProject)},
		{"Celery", yesNo(m.useCelery)},
	}

	for _, cfg := range configs {
		key := lipgloss.NewStyle().Foreground(lipgloss.Color("#7D56F4")).Bold(true).Width(20).Render(cfg.key + ":")
		s.WriteString(fmt.Sprintf("%s %s\n", key, cfg.value))
	}

	s.WriteString("\n")

	// Buttons
	confirmBtn := " Confirm & Generate "
	backBtn := " Go Back "

	if m.cursor == 0 {
		confirmBtn = selectedStyle.Render("▸ " + confirmBtn)
		backBtn = "  " + backBtn
	} else {
		confirmBtn = "  " + confirmBtn
		backBtn = selectedStyle.Render("▸ " + backBtn)
	}

	s.WriteString(confirmBtn)
	s.WriteString("  ")
	s.WriteString(backBtn)
	s.WriteString("\n\n")
	s.WriteString(helpStyle.Render("Tab/Space: Switch • Enter: Select • Ctrl+C: Quit"))

	return s.String()
}

func (m model) renderExecuting() string {
	var s strings.Builder
	s.WriteString(titleStyle.Render("🔨 Generating Your Project..."))
	s.WriteString("\n\n")
	s.WriteString("This may take a minute while we:\n\n")
	s.WriteString("  • Create Python virtual environment\n")
	s.WriteString("  • Install cookiecutter\n")
	s.WriteString("  • Generate project from template\n")
	s.WriteString("\n")
	s.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("#7D56F4")).Render("⠋ Please wait..."))
	return s.String()
}

func (m model) renderDone() string {
	var s strings.Builder

	if m.executionError != nil {
		s.WriteString(errorStyle.Render("❌ Error"))
		s.WriteString("\n\n")
		s.WriteString(fmt.Sprintf("Failed to generate project: %v\n\n", m.executionError))
		if m.executionOutput != "" {
			s.WriteString("Output:\n")
			s.WriteString(m.executionOutput)
			s.WriteString("\n")
		}
	} else {
		s.WriteString(successStyle.Render("✨ Success!"))
		s.WriteString("\n\n")
		s.WriteString(fmt.Sprintf("Your project '%s' has been created successfully!\n\n", m.projectName))

		projectSlug := strings.ToLower(strings.ReplaceAll(m.projectName, " ", "-"))

		s.WriteString(focusedStyle.Render("Next steps:"))
		s.WriteString("\n\n")
		s.WriteString(fmt.Sprintf("  cd %s\n", projectSlug))

		if m.useDocker {
			s.WriteString("  cp .env.example .env.local\n")
			s.WriteString("  # Edit .env.local with your settings\n")
			s.WriteString("  docker-compose up\n\n")
			s.WriteString("Your API will be available at:\n")
			s.WriteString(fmt.Sprintf("  • Backend: http://localhost:%s\n", m.backendPort))
			s.WriteString(fmt.Sprintf("  • API Docs: http://localhost:%s/docs\n", m.backendPort))
		} else {
			s.WriteString("  cd backend\n")
			s.WriteString("  python -m venv .venv\n")
			s.WriteString("  source .venv/bin/activate\n")
			s.WriteString("  pip install -r requirements.txt\n")
			s.WriteString(fmt.Sprintf("  uvicorn app.main:app --reload --port %s\n", m.backendPort))
		}
	}

	s.WriteString("\n")
	s.WriteString(helpStyle.Render("Press Enter or q to exit"))
	return s.String()
}

func (m model) executeSetup() tea.Cmd {
	return func() tea.Msg {
		// Prepare cookiecutter variables
		projectSlug := strings.ToLower(strings.ReplaceAll(m.projectName, " ", "-"))

		// Create virtual environment
		venvCmd := exec.Command("python3", "-m", "venv", ".venv")
		if output, err := venvCmd.CombinedOutput(); err != nil {
			return executionCompleteMsg{
				output: string(output),
				err:    fmt.Errorf("failed to create venv: %w", err),
			}
		}

		// Install cookiecutter
		pipCmd := exec.Command(".venv/bin/pip", "install", "cookiecutter")
		if output, err := pipCmd.CombinedOutput(); err != nil {
			return executionCompleteMsg{
				output: string(output),
				err:    fmt.Errorf("failed to install cookiecutter: %w", err),
			}
		}

		// Get the template from GitHub
		templateGithubURL := "https://github.com/thalestmm/fastapi-cookiecutter-template.git"

		// Build cookiecutter command with all variables passed as arguments
		cookiecutterCmd := exec.Command(
			".venv/bin/cookiecutter",
			templateGithubURL,
			"--no-input",
			"--overwrite-if-exists",
			"project_name="+m.projectName,
			"project_slug="+projectSlug,
			"project_description="+m.projectDescription,
			"author="+m.author,
			"email="+m.email,
			"python_version="+m.pythonVersion,
			"backend_port="+m.backendPort,
			"use_postgres="+yesNo(m.usePostgres),
			"use_supabase="+yesNo(m.useSupabase),
			"ai_project="+yesNo(m.aiProject),
			"use_celery="+yesNo(m.useCelery),
			"use_docker="+yesNo(m.useDocker),
		)

		output, err := cookiecutterCmd.CombinedOutput()
		if err != nil {
			return executionCompleteMsg{
				output: string(output),
				err:    fmt.Errorf("failed to run cookiecutter: %w", err),
			}
		}

		return executionCompleteMsg{
			output: string(output),
			err:    nil,
		}
	}
}

func yesNo(b bool) string {
	if b {
		return "y"
	}
	return "n"
}

func main() {
	p := tea.NewProgram(initialModel())
	if _, err := p.Run(); err != nil {
		fmt.Println("Error running program:", err)
		os.Exit(1)
	}
}
