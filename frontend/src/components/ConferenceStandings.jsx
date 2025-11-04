import React from 'react'
import './ConferenceStandings.css'

function ConferenceStandings({ conference, teams }) {
  const formatWinPct = (pct) => {
    if (isNaN(pct) || pct === null) return '0.000'
    return pct.toFixed(3)
  }

  // Sort teams by win percentage (descending)
  const sortedTeams = [...teams].sort((a, b) => b.win_pct - a.win_pct)

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
          {sortedTeams.map((team, index) => (
            <tr key={team.team} className={index === 0 ? 'leader' : ''}>
              <td className="rank">{index + 1}</td>
              <td className="team-name">
                <span className="team-abbr">{team.team}</span>
                <span className="team-full">{team.name}</span>
              </td>
              <td className="division-name">{team.division}</td>
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

export default ConferenceStandings

