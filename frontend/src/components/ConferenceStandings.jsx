import React, { useState, useEffect } from 'react'
import './ConferenceStandings.css'

function ConferenceStandings({ conference, teams, season, API_URL, expandTeam, onExpandProcessed }) {
  const [expandedTeam, setExpandedTeam] = useState(null)
  const [gameScores, setGameScores] = useState({})
  const [loadingScores, setLoadingScores] = useState({})

  // Clear expanded state when season changes
  useEffect(() => {
    setExpandedTeam(null)
    setGameScores({})
    setLoadingScores({})
  }, [season])

  // Handle external expand request
  useEffect(() => {
    if (expandTeam && expandTeam !== expandedTeam) {
      const team = teams.find(t => t.team === expandTeam)
      if (team) {
        // Expand the team
        setExpandedTeam(expandTeam)
        
        // Notify parent that we've processed the expand request
        if (onExpandProcessed) {
          onExpandProcessed()
        }
        
        // Fetch game scores if not already loaded
        if (!gameScores[expandTeam] && season) {
          // Start loading
          setLoadingScores(prev => ({ ...prev, [expandTeam]: true }))
          
          // Fetch game scores
          const baseUrl = API_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : '')
          const url = `${baseUrl}/api/game-scores?team=${expandTeam}&season=${season}`
          
          fetch(url)
            .then(response => {
              if (!response.ok) {
                throw new Error(`Failed to fetch game scores: ${response.status}`)
              }
              return response.json()
            })
            .then(data => {
              setGameScores(prev => ({ ...prev, [expandTeam]: data.game_scores || [] }))
            })
            .catch(err => {
              console.error('Error fetching game scores:', err)
              setGameScores(prev => ({ ...prev, [expandTeam]: [] }))
            })
            .finally(() => {
              setLoadingScores(prev => ({ ...prev, [expandTeam]: false }))
            })
        }
      }
    }
  }, [expandTeam, expandedTeam, teams, gameScores, season, API_URL, onExpandProcessed])

  const formatWinPct = (pct) => {
    if (isNaN(pct) || pct === null) return '0.000'
    return pct.toFixed(3)
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  const handleTeamClick = async (team) => {
    if (expandedTeam === team.team) {
      // Collapse if already expanded
      setExpandedTeam(null)
      return
    }

    // Expand the clicked team
    setExpandedTeam(team.team)

    // If we already have the scores, don't fetch again
    if (gameScores[team.team]) {
      return
    }

    // Fetch game scores
    if (!season) {
      console.warn('No season available to fetch game scores')
      return
    }

    setLoadingScores(prev => ({ ...prev, [team.team]: true }))
    
    try {
      // Use API_URL if set, otherwise default to localhost:8000 for local development
      const baseUrl = API_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : '')
      const url = `${baseUrl}/api/game-scores?team=${team.team}&season=${season}`
      console.log('Fetching game scores from:', url)
      const response = await fetch(url)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('API error response:', errorText)
        throw new Error(`Failed to fetch game scores: ${response.status} ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('Game scores response:', data)
      setGameScores(prev => ({ ...prev, [team.team]: data.game_scores || [] }))
    } catch (err) {
      console.error('Error fetching game scores:', err)
      setGameScores(prev => ({ ...prev, [team.team]: [] }))
    } finally {
      setLoadingScores(prev => ({ ...prev, [team.team]: false }))
    }
  }

  // Sort teams by win percentage, then by in-division win percentage as tiebreaker
  const sortedTeams = [...teams].sort((a, b) => {
    // First sort by overall win percentage (descending)
    if (b.win_pct !== a.win_pct) {
      return b.win_pct - a.win_pct
    }
    // If tied, use in-division win percentage as tiebreaker (descending)
    const aDivPct = a.in_division_win_pct || 0
    const bDivPct = b.in_division_win_pct || 0
    return bDivPct - aDivPct
  })

  return (
    <div className="conference-standings">
      <h3 className="conference-standings-title">Overall {conference} Conference Standings</h3>
      <table className="conference-standings-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Team</th>
            <th>Division</th>
            <th>W</th>
            <th>L</th>
            <th>T</th>
            <th>Pct</th>
          </tr>
        </thead>
        <tbody>
          {sortedTeams.map((team, index) => {
            const isExpanded = expandedTeam === team.team
            const teamScores = gameScores[team.team] || []
            const isLoading = loadingScores[team.team] || false

            return (
              <React.Fragment key={team.team}>
                <tr 
                  id={`team-${conference}-${team.team}`.replace(/\s+/g, '-')}
                  className={`${index === 0 ? 'leader' : ''} ${isExpanded ? 'expanded' : ''} clickable-row`}
                  onClick={() => handleTeamClick(team)}
                  style={{ cursor: 'pointer' }}
                >
                  <td className="rank">{index + 1}</td>
                  <td className={`team-name ${isExpanded ? 'expanded' : ''}`}>
                    <span className="team-abbr">
                      {team.team}
                      <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                    </span>
                    <span className="team-full">{team.name}</span>
                  </td>
                  <td className="division-name">{team.division}</td>
                  <td>{team.wins}</td>
                  <td>{team.losses}</td>
                  <td>{team.ties}</td>
                  <td className="win-pct">{formatWinPct(team.win_pct)}</td>
                </tr>
                {isExpanded && (
                  <tr className="game-scores-row">
                    <td colSpan="7" className="game-scores-cell">
                      {isLoading ? (
                        <div className="loading-scores">Loading game scores...</div>
                      ) : teamScores.length === 0 ? (
                        <div className="no-scores">
                          <div>No game scores available for {team.team} in {season}</div>
                          <div className="no-scores-hint">Game scores will appear after running a data scrape.</div>
                        </div>
                      ) : (
                        <div className="game-scores-container">
                          <table className="game-scores-table">
                            <thead>
                              <tr>
                                <th>Date</th>
                                <th>Opponent</th>
                                <th>Score</th>
                                <th>Result</th>
                              </tr>
                            </thead>
                            <tbody>
                              {teamScores.map((game) => (
                                <tr key={game.id} className={`${game.is_win ? 'win' : game.is_loss ? 'loss' : 'tie'} ${game.is_division_game ? 'division-game' : ''}`}>
                                  <td>{formatDate(game.gameday)}</td>
                                  <td className="opponent">
                                    {game.opponent || '-'}
                                    {game.is_division_game && (
                                      <span className="division-badge" title="Division game">DIV</span>
                                    )}
                                  </td>
                                  <td className="score">
                                    {game.score} - {game.opponent_score || '-'}
                                  </td>
                                  <td className="result">
                                    {game.is_win ? 'W' : game.is_loss ? 'L' : 'T'}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default ConferenceStandings

