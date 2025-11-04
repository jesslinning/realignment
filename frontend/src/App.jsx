import React, { useState, useEffect } from 'react'
import StandingsDisplay from './components/StandingsDisplay'
import './App.css'

function App() {
  const [standings, setStandings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [season, setSeason] = useState(null)
  const [availableSeasons, setAvailableSeasons] = useState([])

  // Fetch available seasons on mount
  useEffect(() => {
    fetchAvailableSeasons()
  }, [])

  // Update page title when season changes
  useEffect(() => {
    if (season) {
      document.title = `${season} NFL Standings`
    } else {
      document.title = 'NFL Standings'
    }
  }, [season])

  // Fetch standings when season changes
  useEffect(() => {
    if (season !== null) {
      fetchStandings()
    }
  }, [season])

  const fetchAvailableSeasons = async () => {
    try {
      const response = await fetch('/api/seasons')
      if (!response.ok) {
        throw new Error('Failed to fetch available seasons')
      }
      const data = await response.json()
      const seasons = data.seasons || []
      setAvailableSeasons(seasons)
      // Set default season to most recent (first in descending list)
      if (seasons.length > 0 && season === null) {
        setSeason(seasons[0])
      }
    } catch (err) {
      console.error('Error fetching available seasons:', err)
      // If we can't get seasons, try to use current year
      const currentYear = new Date().getFullYear()
      setAvailableSeasons([currentYear])
      setSeason(currentYear)
    }
  }

  const fetchStandings = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/standings?season=${season}`)
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Server error: ${response.status} ${response.statusText}`)
      }
      const data = await response.json()
      setStandings(data)
    } catch (err) {
      // Check if it's a network error (backend not running)
      if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        setError('Cannot connect to backend server. Make sure the backend is running on http://localhost:8000')
      } else {
        setError(err.message)
      }
      console.error('Error fetching standings:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>{season ? `${season} NFL Standings` : 'NFL Standings'}</h1>
        <div className="season-selector">
          <label htmlFor="season">Season: </label>
          <select
            id="season"
            value={season || ''}
            onChange={(e) => setSeason(parseInt(e.target.value))}
            className="season-dropdown"
          >
            {availableSeasons.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </header>
      
      <main>
        {loading && <div className="loading">Loading standings...</div>}
        {error && <div className="error">Error: {error}</div>}
        {standings && !loading && <StandingsDisplay standings={standings} />}
      </main>
    </div>
  )
}

export default App

