
import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [activePage, setActivePage] = useState('Dashboard')
  const [authMode, setAuthMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState(() => localStorage.getItem('careerai_token') || '')
  const [userEmail, setUserEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('error')
  const [jobs, setJobs] = useState([])
  const [jobsLoading, setJobsLoading] = useState(false)
  const [jobsError, setJobsError] = useState('')
  const [jobsRefresh, setJobsRefresh] = useState(0)

  async function handleAuth(event) {
    event.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const endpoint = authMode === 'login' ? '/api/login' : '/api/register'
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      const data = await response.json()

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(', ')
          : data.detail
        throw new Error(detail || 'Something went wrong. Please try again.')
      }

      if (authMode === 'register') {
        setMessageType('success')
        setMessage('Registration successful! Please log in.')
        setAuthMode('login')
        setPassword('')
      } else {
        localStorage.setItem('careerai_token', data.access_token)
        setToken(data.access_token)
        setUserEmail(data.user?.email || email)
        setMessage('')
      }
    } catch (error) {
      setMessageType('error')
      setMessage(error.message || 'Could not connect to the server.')
    } finally {
      setLoading(false)
    }
  }

  function handleLogout() {
    localStorage.removeItem('careerai_token')
    setToken('')
    setUserEmail('')
    setPassword('')
    setEmail('')
    setActivePage('Dashboard')
    setMessage('')
  }

  useEffect(() => {
    if (!token) return
    let cancelled = false

    async function checkSession() {
      try {
        const response = await fetch('/api/profile', {
          headers: { Authorization: `Bearer ${token}` },
        })

        if (!response.ok) {
          localStorage.removeItem('careerai_token')
          if (!cancelled) {
            setToken('')
            setUserEmail('')
          }
          return
        }

        const data = await response.json()
        if (!cancelled) {
          setUserEmail(data.user?.email || data.email || '')
        }
      } catch {
        if (!cancelled) {
          setMessageType('error')
          setMessage('Cannot reach the backend. Check that your server is running.')
        }
      }
    }

    checkSession()
    return () => {
      cancelled = true
    }
  }, [token])

  useEffect(() => {
    if (!token || activePage !== 'Find Jobs') return
    let cancelled = false

    async function loadJobs() {
      setJobsLoading(true)
      setJobsError('')

      try {
        const response = await fetch('/api/jobs')
        if (!response.ok) {
          throw new Error(`Could not load jobs (HTTP ${response.status}).`)
        }

        const data = await response.json()
        if (!Array.isArray(data)) {
          throw new Error('The jobs API returned an unexpected response.')
        }

        if (!cancelled) setJobs(data)
      } catch (error) {
        if (!cancelled) {
          setJobsError(error.message || 'Could not load jobs. Check the backend server.')
        }
      } finally {
        if (!cancelled) setJobsLoading(false)
      }
    }

    loadJobs()
    return () => {
      cancelled = true
    }
  }, [token, activePage, jobsRefresh])

  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-decoration auth-decoration-one" />
        <div className="auth-decoration auth-decoration-two" />
        <section className="auth-card">
          <div className="brand auth-brand">
            <div className="brand-icon">CA</div>
            <div>
              <h2>CareerAI</h2>
              <span>STUDENT ASSISTANT</span>
            </div>
          </div>

          <p className="eyebrow">YOUR PERSONAL CAREER COMPANION</p>
          <h1>{authMode === 'login' ? 'Welcome back!' : 'Start your journey.'}</h1>
          <p className="auth-description">
            {authMode === 'login'
              ? 'Log in to continue building your career.'
              : 'Create your account and explore new opportunities.'}
          </p>

          <form className="auth-form" onSubmit={handleAuth}>
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              autoComplete="email"
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={8}
              maxLength={128}
              autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
            />

            {message && (
              <p className={`auth-message ${messageType}`} role="alert">
                {message}
              </p>
            )}

            <button className="primary-button auth-submit" type="submit" disabled={loading}>
              {loading ? 'Please wait...' : authMode === 'login' ? 'Log in →' : 'Create account →'}
            </button>
          </form>

          <p className="auth-switch">
            {authMode === 'login' ? "Don't have an account?" : 'Already have an account?'}{' '}
            <button
              type="button"
              className="auth-link"
              onClick={() => {
                setAuthMode(authMode === 'login' ? 'register' : 'login')
                setMessage('')
              }}
            >
              {authMode === 'login' ? 'Register' : 'Log in'}
            </button>
          </p>

          <p className="auth-note">Your next opportunity starts with one small step.</p>
        </section>
      </div>
    )
  }

  const menuItems = [
    { name: 'Dashboard', icon: '⌂' },
    { name: 'My Profile', icon: '♙' },
    { name: 'Find Jobs', icon: '⌕' },
    { name: 'Career Guidance', icon: '✧' },
    { name: 'Skill Gap', icon: '◎' },
    { name: 'Resume Assistant', icon: '▤' },
  
  ]



  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">CA</div>
          <div>
            <h2>CareerAI</h2>
            <span>STUDENT ASSISTANT</span>
          </div>
        </div>

        <p className="menu-label">WORKSPACE</p>
        <nav className="sidebar-menu">
          {menuItems.map((item) => (
            <button
              key={item.name}
              className={`menu-item ${activePage === item.name ? 'active' : ''}`}
              onClick={() => setActivePage(item.name)}
            >
              <span className="menu-icon">{item.icon}</span>
              {item.name}
              {item.name === 'Find Jobs' && <span className="menu-badge">NEW</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">✦</div>
            <h3>Build your future</h3>
            <p>Small steps today, big opportunities tomorrow.</p>
          </div>

          <div className="user-mini">
            <div className="avatar">{userEmail ? userEmail[0].toUpperCase() : 'S'}</div>
            <div className="user-details">
              <strong>{userEmail || 'Student'}</strong>
              <span>Career explorer</span>
            </div>
          </div>

          <button className="logout-button" onClick={handleLogout}>Log out</button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{activePage}</strong>
          </div>
          <div className="topbar-right">
            <span className="status-dot" />
            <span>Career journey</span>
            <div className="avatar">{userEmail ? userEmail[0].toUpperCase() : 'S'}</div>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome-row">
            <div>
              <p className="eyebrow">YOUR PERSONAL CAREER COMPANION</p>
              <h1>
                {activePage === 'Dashboard' ? <>Your future starts <span>here.</span></> : activePage}
              </h1>
              <p className="welcome-description">
                Discover opportunities, understand your skills, and take the next step toward your dream career.
              </p>
            </div>
            <div className="date-chip">✦ &nbsp; YOUR GROWTH SPACE</div>
          </section>

          {activePage === 'Dashboard' ? (
            <>
              <section className="hero-card">
                <div className="hero-content">
                  <span className="hero-tag">✦ YOUR NEXT CHAPTER</span>
                  <h2>Turn your skills into opportunities.</h2>
                  <p>
                    Explore career paths, discover relevant jobs, and find the skills that can move you forward.
                  </p>
                  <button className="primary-button" onClick={() => setActivePage('Career Guidance')}>
                    Explore my career <span>→</span>
                  </button>
                </div>
                <div className="hero-art" aria-hidden="true">
                  <div className="orbit orbit-one" />
                  <div className="orbit orbit-two" />
                  <div className="art-card">
                    <div className="art-sparkle">✦</div>
                    <div className="art-bars"><i /><i /><i /><i /><i /></div>
                    <span>GROWTH IN PROGRESS</span>
                  </div>
                  <div className="floating-star star-one">✦</div>
                  <div className="floating-star star-two">✧</div>
                </div>
              </section>

              <section className="section-heading">
                <div>
                  <h2>Your career workspace</h2>
                  <p>Everything you need to move forward.</p>
                </div>
              </section>

              <section className="feature-grid">
                <button className="feature-card" onClick={() => setActivePage('Find Jobs')}>
                  <div className="feature-icon purple">↗</div>
                  <span className="feature-kicker">OPPORTUNITIES</span>
                  <h3>Jobs & Internships</h3>
                  <p>Discover roles that match your interests and skills.</p>
                  <span className="feature-link">Explore opportunities →</span>
                </button>

                <button className="feature-card" onClick={() => setActivePage('Skill Gap')}>
                  <div className="feature-icon green">◎</div>
                  <span className="feature-kicker">YOUR GROWTH</span>
                  <h3>Skill Gap Analysis</h3>
                  <p>Understand which skills to develop for your target role.</p>
                  <span className="feature-link">Check my skills →</span>
                </button>

                <button className="feature-card" onClick={() => setActivePage('Career Guidance')}>
                  <div className="feature-icon orange">✧</div>
                  <span className="feature-kicker">YOUR DIRECTION</span>
                  <h3>Career Guidance</h3>
                  <p>Explore career paths based on your skill set.</p>
                  <span className="feature-link">Explore careers →</span>
                </button>
              </section>

              <section className="bottom-grid">
                <div className="panel profile-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Build your profile</h3>
                      <p>A stronger profile helps personalize your journey.</p>
                    </div>
                    <div className="small-icon">♙</div>
                  </div>
                  <div className="profile-progress">
                    <div className="progress-track"><div className="progress-fill" /></div>
                    <span>Getting started</span>
                  </div>
                  <button className="secondary-button" onClick={() => setActivePage('My Profile')}>
                    Complete my profile →
                  </button>
                </div>

                <div className="panel resume-panel">
                  <div className="resume-decoration">▤</div>
                  <div>
                    <span className="feature-kicker">CAREER TOOLKIT</span>
                    <h3>Your resume, your story.</h3>
                    <p>Prepare to present your skills and experience.</p>
                    <button className="text-button" onClick={() => setActivePage('Resume Assistant')}>
                      Open resume assistant →
                    </button>
                  </div>
                </div>
              </section>
            </>
          ) : activePage === 'Find Jobs' ? (
            <section className="jobs-section">
              <div className="section-heading jobs-heading">
                <div>
                  <h2>Jobs & Internships</h2>
                  <p>Opportunities currently stored in the CareerAI database.</p>
                </div>
                <button className="secondary-button" onClick={() => setJobsRefresh((value) => value + 1)}>
                  Refresh jobs ↻
                </button>
              </div>

              {jobsLoading ? (
                <div className="panel jobs-state">Loading jobs from the backend...</div>
              ) : jobsError ? (
                <div className="panel jobs-state jobs-error">
                  <h3>Could not load jobs</h3>
                  <p>{jobsError}</p>
                  <button className="secondary-button" onClick={() => setActivePage('Dashboard')}>
                    Back to dashboard
                  </button>
                </div>
              ) : jobs.length === 0 ? (
                <div className="panel jobs-state">
                  <h3>No jobs found yet</h3>
                  <p>Add a job through the backend Swagger page, then return here.</p>
                </div>
              ) : (
                <>
                  <p className="jobs-count">
                    {jobs.length} listing{jobs.length === 1 ? '' : 's'} from your database
                  </p>
                  <div className="jobs-grid">
                    {jobs.map((job) => (
                      <article className="panel job-card" key={job.id}>
                        <div className="job-card-top">
                          <div className="job-company-icon">
                            {(job.company || 'J').trim().charAt(0).toUpperCase()}
                          </div>
                          <span className="job-type">{job.job_type || 'Opportunity'}</span>
                        </div>
                        <h3>{job.title || 'Untitled role'}</h3>
                        <p className="job-company">{job.company || 'Company not specified'}</p>
                        <p className="job-location">⌖ &nbsp; {job.location || 'Location not specified'}</p>
                        <div className="job-skills">
                          <strong>Required skills</strong>
                          <p>{job.required_skills || 'Not specified'}</p>
                        </div>
                        <a
                          className="primary-button job-apply"
                          href={job.apply_link}
                          target="_blank"
                          rel="noreferrer"
                        >
                          View / Apply ↗
                        </a>
                      </article>
                    ))}
                  </div>
                  <p className="demo-data-note">
                    Note: listings are currently database test records. Verify each employer and application link before treating a listing as a real opportunity.
                  </p>
                </>
              )}
            </section>
          ) : (
            <section className="panel placeholder-panel">
              <div className="placeholder-icon">✦</div>
              <h2>{activePage}</h2>
              <p>
                This section is part of your CareerAI workspace. We will connect it to the backend and implement its functionality step by step.
              </p>
              <button className="secondary-button" onClick={() => setActivePage('Dashboard')}>
                ← Back to dashboard
              </button>
            </section>
          )}

          <footer className="page-footer">
            <span>CareerAI · Student Career Assistant</span>
            <span>Designed for your next opportunity ✦</span>
          </footer>
        </div>
      </main>
    </div>
  )

}
export default App

