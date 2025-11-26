import React, { useState, useEffect, useMemo } from 'react'
import DivisionStandings from './DivisionStandings'
import ConferenceStandings from './ConferenceStandings'
import PlayoffStandings from './PlayoffStandings'
import './StandingsDisplay.css'

// Define custom division order for each conference
const divisionOrder = {
  'Animals': ['Animals Who Eat Fish', 'Animals Who Eat Grass', "Birds Who Can't Swim", 'Cats'],
  'People': ['People', 'People with Jobs', 'Violent People', 'Fictional People']
}

// Get divisions in the correct order for a conference
const getOrderedDivisions = (conference, standings) => {
  if (!conference || !standings[conference]) return []
  
  const divisions = Object.keys(standings[conference])
  const customOrder = divisionOrder[conference] || []
  
  if (customOrder.length === 0) {
    // No custom order, return sorted alphabetically
    return divisions.sort()
  }
  
  // Sort divisions according to custom order
  return divisions.sort((a, b) => {
    const indexA = customOrder.indexOf(a)
    const indexB = customOrder.indexOf(b)
    
    // If both are in custom order, sort by their position
    if (indexA !== -1 && indexB !== -1) {
      return indexA - indexB
    }
    // If only one is in custom order, it comes first
    if (indexA !== -1) return -1
    if (indexB !== -1) return 1
    // If neither is in custom order, sort alphabetically
    return a.localeCompare(b)
  })
}

function StandingsDisplay({ standings, season, API_URL }) {
  const conferences = Object.keys(standings).sort()
  const [activeConference, setActiveConference] = useState(conferences[0] || '')
  const [scrollToTeam, setScrollToTeam] = useState(null)
  const [expandTeam, setExpandTeam] = useState(null)

  // Reset active conference when standings data changes
  useEffect(() => {
    if (conferences.length > 0 && !conferences.includes(activeConference)) {
      setActiveConference(conferences[0])
    }
  }, [conferences, activeConference])

  // Get ordered divisions for the active conference
  const orderedDivisions = useMemo(() => {
    return getOrderedDivisions(activeConference, standings)
  }, [activeConference, standings])

  // Combine all teams from all divisions in the active conference
  const allConferenceTeams = useMemo(() => {
    if (!activeConference || !standings[activeConference]) return []
    
    const allTeams = []
    
    orderedDivisions.forEach((division) => {
      standings[activeConference][division].forEach((team) => {
        allTeams.push({
          ...team,
          division: division
        })
      })
    })
    
    return allTeams
  }, [activeConference, standings, orderedDivisions])

  // Handle scrolling to a division
  const handleScrollToDivision = (division) => {
    const divisionId = `division-${activeConference}-${division}`.replace(/\s+/g, '-')
    const element = document.getElementById(divisionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      // Add a highlight effect
      element.style.transition = 'background-color 0.3s'
      element.style.backgroundColor = '#fff8e1'
      setTimeout(() => {
        element.style.backgroundColor = ''
      }, 2000)
    }
  }

  // Handle scrolling to a team in overall standings and expanding it
  const handleScrollToTeam = (teamAbbr) => {
    setExpandTeam(teamAbbr)
    setScrollToTeam(teamAbbr)
  }

  // Effect to scroll to team after state updates
  useEffect(() => {
    if (scrollToTeam) {
      const teamId = `team-${activeConference}-${scrollToTeam}`.replace(/\s+/g, '-')
      const element = document.getElementById(teamId)
      if (element) {
        // Small delay to ensure DOM is updated
        setTimeout(() => {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' })
          // Add a highlight effect
          element.style.transition = 'background-color 0.3s'
          element.style.backgroundColor = '#e3f2fd'
          setTimeout(() => {
            element.style.backgroundColor = ''
          }, 2000)
        }, 100)
      }
      setScrollToTeam(null)
    }
  }, [scrollToTeam, activeConference])

  if (conferences.length === 0) {
    return <div className="standings-display">No standings available</div>
  }

  return (
    <div className="standings-display">
      <div className="tabs">
        {conferences.map((conference) => (
          <button
            key={conference}
            className={`tab ${activeConference === conference ? 'active' : ''}`}
            onClick={() => setActiveConference(conference)}
          >
            {conference} Conference
          </button>
        ))}
      </div>
      
      <div className="conference-content">
        <PlayoffStandings
          conference={activeConference}
          standings={standings}
          onTeamClick={handleScrollToDivision}
        />
        
        <div className="conference">
          <div className="divisions">
            {orderedDivisions.map((division) => (
              <DivisionStandings
                key={division}
                conference={activeConference}
                division={division}
                teams={standings[activeConference][division]}
                onTeamClick={handleScrollToTeam}
              />
            ))}
          </div>
        </div>
        
        <ConferenceStandings
          conference={activeConference}
          teams={allConferenceTeams}
          season={season}
          API_URL={API_URL}
          expandTeam={expandTeam}
          onExpandProcessed={() => setExpandTeam(null)}
        />
      </div>
    </div>
  )
}

export default StandingsDisplay

