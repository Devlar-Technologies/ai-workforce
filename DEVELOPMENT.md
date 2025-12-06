# Devlar AI Workforce - Development Practices

## Core Development Rule: Documentation First

**CRITICAL RULE: Documentation must be updated with every code change. No exceptions.**

### Documentation Update Requirements

For every task completed:

1. **Update relevant documentation in `docs/`**
   - Component documentation when adding/modifying agents or tools
   - API reference when changing interfaces
   - Tutorial updates when changing workflows
   - Architecture updates when changing system design

2. **Update root documentation**
   - `README.md` for major feature changes
   - `CHANGELOG.md` for all changes
   - Any relevant setup or configuration files

3. **Create new documentation**
   - New components require corresponding doc files
   - New workflows need example documentation
   - New integrations need setup guides

### Documentation Standards

- **Always current**: Documentation reflects the actual current state
- **Example-driven**: Include working examples for all features
- **User-focused**: Written for developers who need to use/understand the system
- **Complete**: Cover setup, usage, troubleshooting, and edge cases

### Enforcement

- Every commit should include documentation updates
- PR reviews must verify documentation currency
- No feature is considered complete until docs are updated

## Devlar Context

This project is the **Devlar AI Workforce** - a production-ready hierarchical CrewAI system for Alan O'Meara's company [Devlar.io](https://devlar.io).

### Tone & Style
- **Technical**: Assume developer audience
- **No-BS**: Direct, clear communication
- **Developer-first**: Focus on practical implementation
- **Slightly irreverent**: Professional but not corporate

### Product Context
Devlar builds AI-first SaaS tools including:
- **Chromentum**: Chrome extension for productivity
- **Zeneural**: AI meditation platform
- **TimePost**: Social media scheduling
- **AimStack**: AI development framework
- **Elephant Desktop**: Workspace management

### Technical Standards
- **Wave-based execution**: Parallel + sequential task management
- **Quality control**: GREEN/RED/YELLOW verdicts with retry logic
- **Human-in-the-loop**: Approval for high-cost operations (>$50)
- **Comprehensive logging**: Structured logging with Loguru
- **Error handling**: Graceful degradation and recovery

## Development Workflow

1. **Plan** - Update documentation outline
2. **Implement** - Code + inline documentation
3. **Document** - Complete documentation updates
4. **Test** - Verify both code and documentation
5. **Review** - Ensure documentation accuracy
6. **Commit** - Include docs in commit message

## Documentation Structure

```
docs/
├── README.md                    # Documentation index
├── quick-start.md              # Get started guide
├── architecture.md             # System overview
├── api-reference.md            # Complete API docs
├── configuration.md            # Setup and config
├── components/                 # Component-specific docs
│   ├── ceo-orchestrator.md    # CEO agent documentation
│   ├── pods/                  # Pod-specific documentation
│   ├── memory.md              # Memory system docs
│   └── tools.md               # Tools and integrations
├── deployment/                 # Deployment guides
├── examples/                   # Working examples
├── tutorials/                  # Step-by-step guides
├── development/               # Developer resources
└── reference/                 # Reference materials
```

## Commit Message Format

Include documentation updates in commit messages:

```
feat: Add product development pod with wave-based execution

- Implement ProductDevPod with 4-agent pipeline
- Add wave execution for Idea → Code → Test → Deploy
- Include quality control with retry logic
- Support Chromentum, Zeneural, and AimStack workflows

Documentation updates:
- Add ProductDevPod component documentation
- Update architecture overview with development pipeline
- Add product development examples to tutorials
- Update API reference with new agent endpoints
```

## Session Continuity

To maintain this rule across Claude Code sessions:

1. **Check this file first** - Always review DEVELOPMENT.md at session start
2. **Documentation audit** - Verify docs match current code state
3. **Update as you go** - Don't defer documentation updates
4. **Commit together** - Code and docs in same commits when possible

---

**Remember: Outdated documentation is worse than no documentation. Keep it current!**