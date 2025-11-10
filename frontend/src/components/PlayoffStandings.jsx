import React, { useMemo } from 'react'
import './PlayoffStandings.css'

function PlayoffStandings({ conference, standings }) {
  const formatWinPct = (pct) => {
    if (isNaN(pct) || pct === null) return '0.000'
    return pct.toFixed(3)
  }

  // Calculate playoff standings
  const playoffTeams = useMemo(() => {
    if (!conference || !standings[conference]) return []

    const conferenceData = standings[conference]
    const divisions = Object.keys(conferenceData)
    
    // Get division winners (best team in each division)
    const divisionWinners = divisions.map(division => {
      const teams = [...conferenceData[division]]
      // Sort by win_pct, then in_division_win_pct as tiebreaker
      teams.sort((a, b) => {
        if (b.win_pct !== a.win_pct) {
          return b.win_pct - a.win_pct
        }
        const aDivPct = a.in_division_win_pct || 0
        const bDivPct = b.in_division_win_pct || 0
        return bDivPct - aDivPct
      })
      return {
        ...teams[0],
        division: division,
        isDivisionWinner: true
      }
    })

    // Sort division winners by win_pct for seeding
    divisionWinners.sort((a, b) => {
      if (b.win_pct !== a.win_pct) {
        return b.win_pct - a.win_pct
      }
      const aDivPct = a.in_division_win_pct || 0
      const bDivPct = b.in_division_win_pct || 0
      return bDivPct - aDivPct
    })

    // Get all teams in conference, excluding division winners
    const allTeams = []
    const winnerTeamAbbrs = new Set(divisionWinners.map(w => w.team))
    
    divisions.forEach(division => {
      conferenceData[division].forEach(team => {
        if (!winnerTeamAbbrs.has(team.team)) {
          allTeams.push({
            ...team,
            division: division
          })
        }
      })
    })

    // Sort remaining teams by win_pct, then in_division_win_pct as tiebreaker
    allTeams.sort((a, b) => {
      if (b.win_pct !== a.win_pct) {
        return b.win_pct - a.win_pct
      }
      const aDivPct = a.in_division_win_pct || 0
      const bDivPct = b.in_division_win_pct || 0
      return bDivPct - aDivPct
    })

    // Get top 3 wild cards
    const wildCards = allTeams.slice(0, 3)

    // Combine: division winners (seeds 1-4) + wild cards (seeds 5-7)
    const playoffStandings = [
      ...divisionWinners.map((team, index) => ({
        ...team,
        seed: index + 1,
        type: 'Division Winner'
      })),
      ...wildCards.map((team, index) => ({
        ...team,
        seed: index + 5,
        type: 'Wild Card'
      }))
    ]

    return playoffStandings
  }, [conference, standings])

  if (playoffTeams.length === 0) {
    return null
  }

  return (
    <div className="playoff-standings">
      <h3 className="playoff-standings-title">Playoff Standings</h3>
      <table className="playoff-standings-table">
        <thead>
          <tr>
            <th>Seed</th>
            <th>Team</th>
            <th>Division</th>
            <th>Type</th>
            <th>W</th>
            <th>L</th>
            <th>T</th>
            <th>Pct</th>
          </tr>
        </thead>
        <tbody>
          {playoffTeams.map((team) => (
            <tr 
              key={team.team} 
              className={`${team.isDivisionWinner ? 'division-winner' : 'wild-card'}`}
            >
              <td className="seed">{team.seed}</td>
              <td className="team-name">
                <span className="team-abbr">{team.team}</span>
                <span className="team-full">{team.name}</span>
              </td>
              <td className="division-name">{team.division}</td>
              <td className="team-type">{team.type}</td>
              <td>{team.wins}</td>
              <td>{team.losses}</td>
              <td>{team.ties}</td>
              <td className="win-pct">{formatWinPct(team.win_pct)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default PlayoffStandings

