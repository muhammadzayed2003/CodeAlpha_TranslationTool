import { useEffect, useState } from 'react'
import './App.css'

const LANGUAGES = [
  'English',
  'Urdu',
  'Arabic',
  'Hindi',
  'French',
  'German',
  'Spanish',
  'Chinese',
  'Italian',
  'Portuguese',
  'Russian',
  'Japanese',
  'Korean',
  'Turkish',
  'Dutch',
  'Bengali',
  'Persian',
  'Punjabi',
]

const CUSTOM_LANGUAGE = '**custom**'

const SPEECH_LANGUAGES = {
  English: 'en-US',
  Urdu: 'ur-PK',
  Arabic: 'ar-SA',
  Hindi: 'hi-IN',
  French: 'fr-FR',
  German: 'de-DE',
  Spanish: 'es-ES',
  Chinese: 'zh-CN',
  Italian: 'it-IT',
  Portuguese: 'pt-PT',
  Russian: 'ru-RU',
  Japanese: 'ja-JP',
  Korean: 'ko-KR',
  Turkish: 'tr-TR',
  Dutch: 'nl-NL',
  Bengali: 'bn-BD',
  Persian: 'fa-IR',
  Punjabi: 'pa-IN',
}

function App() {
  const [showIntro, setShowIntro] = useState(true)
  const [introFade, setIntroFade] = useState(false)

  const [token, setToken] = useState(
    localStorage.getItem('translatex_token') || ''
  )

  const [user, setUser] = useState(null)
  const [authMode, setAuthMode] = useState('login')

  const [page, setPage] = useState(
    window.location.hash === '#/history'
      ? 'history'
      : 'translator'
  )

  const [sourceSelection, setSourceSelection] =
    useState('English')

  const [targetSelection, setTargetSelection] =
    useState('Urdu')

  const [sourceCustom, setSourceCustom] = useState('')
  const [targetCustom, setTargetCustom] = useState('')

  const [inputText, setInputText] = useState('')
  const [translatedText, setTranslatedText] = useState('')

  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('Ready')

  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)

  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState('')

  const [loginForm, setLoginForm] = useState({
    email: '',
    password: '',
  })

  const [signupForm, setSignupForm] = useState({
    name: '',
    email: '',
    password: '',
  })

  const sourceLanguage =
    sourceSelection === CUSTOM_LANGUAGE
      ? sourceCustom.trim()
      : sourceSelection

  const targetLanguage =
    targetSelection === CUSTOM_LANGUAGE
      ? targetCustom.trim()
      : targetSelection

  /* =========================================================
     5 SECOND INTRO
  ========================================================= */

  useEffect(() => {
    const fadeTimer = setTimeout(() => {
      setIntroFade(true)
    }, 4300)

    const removeTimer = setTimeout(() => {
      setShowIntro(false)
    }, 5000)

    return () => {
      clearTimeout(fadeTimer)
      clearTimeout(removeTimer)
    }
  }, [])

  useEffect(() => {
    if (token) {
      loadCurrentUser()
    }
  }, [token])

  useEffect(() => {
    const handleHashChange = () => {
      const newPage =
        window.location.hash === '#/history'
          ? 'history'
          : 'translator'

      setPage(newPage)

      if (newPage === 'history' && token) {
        loadHistory()
      }
    }

    window.addEventListener(
      'hashchange',
      handleHashChange
    )

    return () => {
      window.removeEventListener(
        'hashchange',
        handleHashChange
      )
    }
  }, [token])

  const navigate = (destination) => {
    window.location.hash =
      destination === 'history'
        ? '#/history'
        : '#/translator'
  }

  const loadCurrentUser = async () => {
    try {
      const response = await fetch(
        'http://127.0.0.1:5000/api/me',
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        logout(false)
        return
      }

      const data = await response.json()
      setUser(data.user)
    } catch {
      setAuthError(
        'Could not connect to the server.'
      )
    }
  }

  const handleLogin = async (event) => {
    event.preventDefault()

    setAuthLoading(true)
    setAuthError('')

    try {
      const response = await fetch(
        'http://127.0.0.1:5000/api/login',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(loginForm),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Login failed'
        )
      }

      localStorage.setItem(
        'translatex_token',
        data.token
      )

      setToken(data.token)
      setUser(data.user)

      setLoginForm({
        email: '',
        password: '',
      })
    } catch (error) {
      setAuthError(
        error.message || 'Login failed'
      )
    } finally {
      setAuthLoading(false)
    }
  }

  const handleSignup = async (event) => {
    event.preventDefault()

    setAuthLoading(true)
    setAuthError('')

    try {
      const response = await fetch(
        'http://127.0.0.1:5000/api/signup',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(signupForm),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Signup failed'
        )
      }

      localStorage.setItem(
        'translatex_token',
        data.token
      )

      setToken(data.token)
      setUser(data.user)

      setSignupForm({
        name: '',
        email: '',
        password: '',
      })
    } catch (error) {
      setAuthError(
        error.message || 'Signup failed'
      )
    } finally {
      setAuthLoading(false)
    }
  }

  const logout = (clearStorage = true) => {
    if (clearStorage) {
      fetch(
        'http://127.0.0.1:5000/api/logout',
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      ).catch(() => {})
    }

    localStorage.removeItem('translatex_token')

    setToken('')
    setUser(null)
    setHistory([])
    setInputText('')
    setTranslatedText('')
    setStatus('Ready')
    setPage('translator')
  }

  const translateText = async () => {
    if (!inputText.trim()) {
      setStatus(
        'Please enter text to translate'
      )
      return
    }

    if (!sourceLanguage || !targetLanguage) {
      setStatus(
        'Please select both languages'
      )
      return
    }

    setLoading(true)
    setStatus('Translating...')
    setTranslatedText('')

    try {
      const response = await fetch(
        'http://127.0.0.1:5000/api/translate',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            text: inputText,
            source: sourceLanguage,
            target: targetLanguage,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Translation failed'
        )
      }

      setTranslatedText(
        data.translation || ''
      )

      setStatus(
        'Translation completed'
      )
    } catch (error) {
      setStatus(
        error.message ||
          'Translation service unavailable'
      )
    } finally {
      setLoading(false)
    }
  }

  const swapLanguages = () => {
    const currentSourceSelection =
      sourceSelection

    const currentSourceCustom =
      sourceCustom

    setSourceSelection(targetSelection)
    setSourceCustom(targetCustom)

    setTargetSelection(
      currentSourceSelection
    )

    setTargetCustom(
      currentSourceCustom
    )

    setInputText(translatedText)
    setTranslatedText(inputText)
  }

  const clearAll = () => {
    setInputText('')
    setTranslatedText('')
    setStatus('Ready')
  }

  const copyTranslation = async () => {
    if (!translatedText) return

    try {
      await navigator.clipboard.writeText(
        translatedText
      )

      setStatus('Translation copied')
    } catch {
      setStatus('Copy failed')
    }
  }

  const speakTranslation = () => {
    if (
      !translatedText ||
      !window.speechSynthesis
    ) {
      setStatus(
        'Text-to-speech is not supported'
      )
      return
    }

    window.speechSynthesis.cancel()

    const speech =
      new SpeechSynthesisUtterance(
        translatedText
      )

    speech.lang =
      SPEECH_LANGUAGES[targetLanguage] ||
      'en-US'

    speech.rate = 0.9

    window.speechSynthesis.speak(
      speech
    )

    setStatus('Playing translation')
  }

  const loadHistory = async () => {
    if (!token) return

    setHistoryLoading(true)

    try {
      const response = await fetch(
        'http://127.0.0.1:5000/api/history',
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error ||
            'Could not load history'
        )
      }

      setHistory(data.history || [])
    } catch (error) {
      setStatus(
        error.message ||
          'Could not load history'
      )
    } finally {
      setHistoryLoading(false)
    }
  }

  const deleteHistoryItem = async (id) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/history/${id}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error ||
            'Could not delete history'
        )
      }

      setHistory((current) =>
        current.filter(
          (item) => item.id !== id
        )
      )
    } catch (error) {
      setStatus(
        error.message ||
          'Could not delete history'
      )
    }
  }

  const useHistoryTranslation = (item) => {
    setSourceSelection(
      LANGUAGES.includes(
        item.source_language
      )
        ? item.source_language
        : CUSTOM_LANGUAGE
    )

    setTargetSelection(
      LANGUAGES.includes(
        item.target_language
      )
        ? item.target_language
        : CUSTOM_LANGUAGE
    )

    if (
      !LANGUAGES.includes(
        item.source_language
      )
    ) {
      setSourceCustom(
        item.source_language
      )
    } else {
      setSourceCustom('')
    }

    if (
      !LANGUAGES.includes(
        item.target_language
      )
    ) {
      setTargetCustom(
        item.target_language
      )
    } else {
      setTargetCustom('')
    }

    setInputText(item.source_text)
    setTranslatedText(
      item.translated_text
    )

    setStatus(
      'History translation loaded'
    )

    navigate('translator')
  }

  const handleSourceSelection = (value) => {
    setSourceSelection(value)

    if (value !== CUSTOM_LANGUAGE) {
      setSourceCustom('')
    }
  }

  const handleTargetSelection = (value) => {
    setTargetSelection(value)

    if (value !== CUSTOM_LANGUAGE) {
      setTargetCustom('')
    }
  }

  /* =========================================================
     INTRO
  ========================================================= */

  if (showIntro) {
    return (
      <IntroPage fading={introFade} />
    )
  }

  if (!token || !user) {
    return (
      <div className="page-reveal">
        <AuthPage
          mode={authMode}
          setMode={(mode) => {
            setAuthMode(mode)
            setAuthError('')
          }}
          loginForm={loginForm}
          setLoginForm={setLoginForm}
          signupForm={signupForm}
          setSignupForm={setSignupForm}
          onLogin={handleLogin}
          onSignup={handleSignup}
          loading={authLoading}
          error={authError}
        />
      </div>
    )
  }

  if (page === 'history') {
    return (
      <div className="page-reveal">
        <HistoryPage
          user={user}
          history={history}
          loading={historyLoading}
          onLoad={loadHistory}
          onDelete={deleteHistoryItem}
          onUse={useHistoryTranslation}
          onTranslator={() =>
            navigate('translator')
          }
          onLogout={logout}
        />
      </div>
    )
  }

  return (
    <div className="page-reveal">
      <TranslatorPage
        user={user}
        sourceSelection={sourceSelection}
        targetSelection={targetSelection}
        sourceCustom={sourceCustom}
        targetCustom={targetCustom}
        sourceLanguage={sourceLanguage}
        targetLanguage={targetLanguage}
        inputText={inputText}
        translatedText={translatedText}
        loading={loading}
        status={status}
        setSourceSelection={
          handleSourceSelection
        }
        setTargetSelection={
          handleTargetSelection
        }
        setSourceCustom={
          setSourceCustom
        }
        setTargetCustom={
          setTargetCustom
        }
        setInputText={setInputText}
        swapLanguages={swapLanguages}
        translateText={translateText}
        clearAll={clearAll}
        copyTranslation={
          copyTranslation
        }
        speakTranslation={
          speakTranslation
        }
        onHistory={() => {
          navigate('history')
          loadHistory()
        }}
        onLogout={logout}
      />
    </div>
  )
}

/* =========================================================
   INTRO PAGE
========================================================= */

function IntroPage({ fading }) {
  return (
    <div
      className={`intro-screen ${
        fading ? 'intro-fading' : ''
      }`}
    >
      <div className="intro-grid"></div>

      <div className="intro-glow intro-glow-one"></div>
      <div className="intro-glow intro-glow-two"></div>
      <div className="intro-glow intro-glow-three"></div>

      <div className="intro-orbit intro-orbit-one"></div>
      <div className="intro-orbit intro-orbit-two"></div>
      <div className="intro-orbit intro-orbit-three"></div>

      <div className="intro-particle particle-one"></div>
      <div className="intro-particle particle-two"></div>
      <div className="intro-particle particle-three"></div>
      <div className="intro-particle particle-four"></div>
      <div className="intro-particle particle-five"></div>
      <div className="intro-particle particle-six"></div>

      <div className="intro-orbiting intro-item-one">
        <span>文</span>
        <small>Chinese</small>
      </div>

      <div className="intro-orbiting intro-item-two">
        <span>ع</span>
        <small>Arabic</small>
      </div>

      <div className="intro-orbiting intro-item-three">
        <span>अ</span>
        <small>Hindi</small>
      </div>

      <div className="intro-orbiting intro-item-four">
        <span>あ</span>
        <small>Japanese</small>
      </div>

      <div className="intro-orbiting intro-item-five">
        <span>A</span>
        <small>English</small>
      </div>

      <div className="intro-center">
        <div className="intro-logo">
          T
        </div>

        <div className="intro-brand">
          TranslateX
        </div>

        <div className="intro-subtitle">
          AI TRANSLATION PLATFORM
        </div>

        <div className="intro-line">
          <span></span>
        </div>

        <div className="intro-status">
          <i></i>
          Initializing intelligent translation
        </div>
      </div>
    </div>
  )
}

function AuthPage({
  mode,
  setMode,
  loginForm,
  setLoginForm,
  signupForm,
  setSignupForm,
  onLogin,
  onSignup,
  loading,
  error,
}) {
  return (
    <div className="auth-page">
      <div className="auth-background">
        <div className="auth-orb auth-orb-one"></div>
        <div className="auth-orb auth-orb-two"></div>
      </div>

      <div className="auth-card">
        <div className="auth-brand">
          <div className="logo-box">
            T
          </div>

          <div>
            <h1>TranslateX</h1>
            <span>
              AI Translation Platform
            </span>
          </div>
        </div>

        <div className="auth-heading">
          <span>
            ✦ INTELLIGENT TRANSLATION
          </span>

          <h2>
            {mode === 'login'
              ? 'Welcome back.'
              : 'Create your account.'}
          </h2>

          <p>
            {mode === 'login'
              ? 'Sign in to continue translating with AI.'
              : 'Create your TranslateX account and start translating.'}
          </p>
        </div>

        <div className="auth-tabs">
          <button
            className={
              mode === 'login'
                ? 'active'
                : ''
            }
            onClick={() =>
              setMode('login')
            }
          >
            Login
          </button>

          <button
            className={
              mode === 'signup'
                ? 'active'
                : ''
            }
            onClick={() =>
              setMode('signup')
            }
          >
            Create Account
          </button>
        </div>

        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        {mode === 'login' ? (
          <form
            onSubmit={onLogin}
            className="auth-form"
          >
            <label>
              Email

              <input
                type="email"
                value={loginForm.email}
                placeholder="you@example.com"
                onChange={(e) =>
                  setLoginForm({
                    ...loginForm,
                    email:
                      e.target.value,
                  })
                }
                required
              />
            </label>

            <label>
              Password

              <input
                type="password"
                value={
                  loginForm.password
                }
                placeholder="Enter your password"
                onChange={(e) =>
                  setLoginForm({
                    ...loginForm,
                    password:
                      e.target.value,
                  })
                }
                required
              />
            </label>

            <button
              className="auth-submit"
              type="submit"
              disabled={loading}
            >
              {loading
                ? 'Signing in...'
                : 'Sign In →'}
            </button>
          </form>
        ) : (
          <form
            onSubmit={onSignup}
            className="auth-form"
          >
            <label>
              Full Name

              <input
                type="text"
                value={signupForm.name}
                placeholder="Your name"
                onChange={(e) =>
                  setSignupForm({
                    ...signupForm,
                    name: e.target.value,
                  })
                }
                required
              />
            </label>

            <label>
              Email

              <input
                type="email"
                value={
                  signupForm.email
                }
                placeholder="you@example.com"
                onChange={(e) =>
                  setSignupForm({
                    ...signupForm,
                    email:
                      e.target.value,
                  })
                }
                required
              />
            </label>

            <label>
              Password

              <input
                type="password"
                value={
                  signupForm.password
                }
                placeholder="Minimum 6 characters"
                onChange={(e) =>
                  setSignupForm({
                    ...signupForm,
                    password:
                      e.target.value,
                  })
                }
                minLength={6}
                required
              />
            </label>

            <button
              className="auth-submit"
              type="submit"
              disabled={loading}
            >
              {loading
                ? 'Creating account...'
                : 'Create Account →'}
            </button>
          </form>
        )}

        <div className="auth-footer">
          <span>
            Secure AI Translation
          </span>

          <span>
            Powered by Gemini
          </span>
        </div>
      </div>
    </div>
  )
}

function TranslatorPage({
  user,
  sourceSelection,
  targetSelection,
  sourceCustom,
  targetCustom,
  sourceLanguage,
  targetLanguage,
  inputText,
  translatedText,
  loading,
  status,
  setSourceSelection,
  setTargetSelection,
  setSourceCustom,
  setTargetCustom,
  setInputText,
  swapLanguages,
  translateText,
  clearAll,
  copyTranslation,
  speakTranslation,
  onHistory,
  onLogout,
}) {
  return (
    <div className="app">
      <div className="background">
        <div className="orb orb-one"></div>
        <div className="orb orb-two"></div>
        <div className="orb orb-three"></div>

        <div className="floating-card card-one">
          <span>文</span>
          <small>Translate</small>
        </div>

        <div className="floating-card card-two">
          <span>ع</span>
          <small>Arabic</small>
        </div>

        <div className="floating-card card-three">
          <span>中</span>
          <small>Chinese</small>
        </div>

        <div className="floating-card card-four">
          <span>أ</span>
          <small>AI</small>
        </div>
      </div>

      <nav className="navbar">
        <div className="logo-area">
          <div className="logo-box">
            T
          </div>

          <div>
            <h2>TranslateX</h2>
            <span>
              AI Translation Platform
            </span>
          </div>
        </div>

        <div className="nav-right">
          <div className="online">
            <span></span>
            AI Online
          </div>

          <button
            className="nav-button"
            onClick={onHistory}
          >
            History
          </button>

          <div className="user-menu">
            <span>{user.name}</span>

            <button onClick={onLogout}>
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main>
        <section className="hero">
          <div className="hero-tag">
            <span>✦</span>
            INTELLIGENT LANGUAGE TRANSLATION
          </div>

          <h1>
            Break the language
            <br />
            <span>
              barrier with AI.
            </span>
          </h1>

          <p>
            Translate conversations, ideas
            and content naturally across
            languages with the power of
            modern AI.
          </p>
        </section>

        <section className="translator-wrapper">
          <div className="translator-top">
            <div className="language-box">
              <span className="label">
                SOURCE LANGUAGE
              </span>

              <select
                value={sourceSelection}
                onChange={(e) =>
                  setSourceSelection(
                    e.target.value
                  )
                }
              >
                {LANGUAGES.map(
                  (language) => (
                    <option
                      key={language}
                      value={language}
                    >
                      {language}
                    </option>
                  )
                )}

                <option
                  value={CUSTOM_LANGUAGE}
                >
                  ✎ Write language name
                </option>
              </select>

              {sourceSelection ===
                CUSTOM_LANGUAGE && (
                <input
                  className="custom-language-input"
                  value={sourceCustom}
                  onChange={(e) =>
                    setSourceCustom(
                      e.target.value
                    )
                  }
                  placeholder="e.g. Kashmiri"
                />
              )}
            </div>

            <button
              className="swap"
              onClick={swapLanguages}
              title="Swap languages"
            >
              ⇄
            </button>

            <div className="language-box">
              <span className="label">
                TARGET LANGUAGE
              </span>

              <select
                value={targetSelection}
                onChange={(e) =>
                  setTargetSelection(
                    e.target.value
                  )
                }
              >
                {LANGUAGES.map(
                  (language) => (
                    <option
                      key={language}
                      value={language}
                    >
                      {language}
                    </option>
                  )
                )}

                <option
                  value={CUSTOM_LANGUAGE}
                >
                  ✎ Write language name
                </option>
              </select>

              {targetSelection ===
                CUSTOM_LANGUAGE && (
                <input
                  className="custom-language-input"
                  value={targetCustom}
                  onChange={(e) =>
                    setTargetCustom(
                      e.target.value
                    )
                  }
                  placeholder="e.g. Pashto"
                />
              )}
            </div>
          </div>

          <div className="translation-area">
            <div className="text-box">
              <div className="text-header">
                <div>
                  <span className="mini-icon">
                    A
                  </span>
                  Original
                </div>

                <span>
                  {sourceLanguage ||
                    'Language'}
                </span>
              </div>

              <textarea
                value={inputText}
                onChange={(e) =>
                  setInputText(
                    e.target.value
                  )
                }
                placeholder="Write something you want to translate..."
                maxLength={5000}
              />

              <div className="text-footer">
                <span>
                  {inputText.length} / 5000
                </span>

                <span>
                  ⌘ Enter to translate
                </span>
              </div>
            </div>

            <div className="text-box result">
              <div className="text-header">
                <div>
                  <span className="mini-icon result-icon">
                    ✦
                  </span>
                  Translation
                </div>

                <span>
                  {targetLanguage ||
                    'Language'}
                </span>
              </div>

              <textarea
                value={translatedText}
                readOnly
                placeholder="Your AI translation will appear here..."
              />

              <div className="text-footer result-footer">
                <span>
                  {loading
                    ? 'AI is translating...'
                    : status}
                </span>

                <div className="result-actions">
                  <button
                    onClick={
                      speakTranslation
                    }
                    disabled={
                      !translatedText
                    }
                    title="Listen"
                  >
                    🔊
                  </button>

                  <button
                    onClick={
                      copyTranslation
                    }
                    disabled={
                      !translatedText
                    }
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="action-area">
            <button
              className="translate-button"
              onClick={translateText}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loader"></span>
                  Translating
                </>
              ) : (
                <>
                  Translate
                  <span className="arrow">
                    →
                  </span>
                </>
              )}
            </button>

            <button
              className="clear-button"
              onClick={clearAll}
            >
              Clear
            </button>
          </div>
        </section>

        <section className="features">
          <div className="feature">
            <div className="feature-symbol">
              ✦
            </div>

            <div>
              <strong>
                AI Powered
              </strong>

              <p>
                Natural context-aware
                translations
              </p>
            </div>
          </div>

          <div className="feature-divider"></div>

          <div className="feature">
            <div className="feature-symbol">
              ◎
            </div>

            <div>
              <strong>
                Every Language
              </strong>

              <p>
                Connect with people
                worldwide
              </p>
            </div>
          </div>

          <div className="feature-divider"></div>

          <div className="feature">
            <div className="feature-symbol">
              ◈
            </div>

            <div>
              <strong>
                Translation History
              </strong>

              <p>
                Your translations stay
                available
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <span>
          © 2026 TranslateX
        </span>

        <span>
          Powered by Gemini
        </span>

        <span>
          CodeAlpha Internship Project
        </span>
      </footer>
    </div>
  )
}

function HistoryPage({
  user,
  history,
  loading,
  onLoad,
  onDelete,
  onUse,
  onTranslator,
  onLogout,
}) {
  return (
    <div className="history-page">
      <nav className="navbar">
        <div className="logo-area">
          <div className="logo-box">
            T
          </div>

          <div>
            <h2>TranslateX</h2>
            <span>
              AI Translation Platform
            </span>
          </div>
        </div>

        <div className="nav-right">
          <div className="online">
            <span></span>
            AI Online
          </div>

          <button
            className="nav-button active-nav"
            onClick={onTranslator}
          >
            Translator
          </button>

          <div className="user-menu">
            <span>{user.name}</span>

            <button onClick={onLogout}>
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="history-main">
        <section className="history-header">
          <div>
            <div className="hero-tag">
              <span>✦</span>
              YOUR TRANSLATIONS
            </div>

            <h1>
              Translation History
            </h1>

            <p>
              View and manage your previous
              AI translations.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={onLoad}
          >
            ↻ Refresh
          </button>
        </section>

        {loading ? (
          <div className="history-empty">
            <div className="loader large-loader"></div>

            <h3>
              Loading history...
            </h3>
          </div>
        ) : history.length === 0 ? (
          <div className="history-empty">
            <div className="empty-icon">
              ◈
            </div>

            <h3>
              No translations yet
            </h3>

            <p>
              Your completed translations
              will appear here.
            </p>

            <button
              className="translate-button"
              onClick={onTranslator}
            >
              Start Translating →
            </button>
          </div>
        ) : (
          <div className="history-list">
            {history.map((item) => (
              <div
                className="history-card"
                key={item.id}
              >
                <div className="history-card-top">
                  <div className="history-languages">
                    <span>
                      {item.source_language}
                    </span>

                    <strong>→</strong>

                    <span>
                      {item.target_language}
                    </span>
                  </div>

                  <div className="history-date">
                    {formatDate(
                      item.created_at
                    )}
                  </div>
                </div>

                <div className="history-content">
                  <div>
                    <small>
                      ORIGINAL
                    </small>

                    <p>
                      {item.source_text}
                    </p>
                  </div>

                  <div>
                    <small>
                      TRANSLATION
                    </small>

                    <p>
                      {item.translated_text}
                    </p>
                  </div>
                </div>

                <div className="history-actions">
                  <button
                    onClick={() =>
                      onUse(item)
                    }
                  >
                    Use Translation
                  </button>

                  <button
                    className="delete-history"
                    onClick={() =>
                      onDelete(item.id)
                    }
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

function formatDate(value) {
  if (!value) return ''

  try {
    return new Date(
      value
    ).toLocaleString()
  } catch {
    return value
  }
}

export default App