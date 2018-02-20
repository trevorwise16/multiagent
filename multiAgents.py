# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)

        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood().asList()
        newGhostStates = successorGameState.getGhostStates()

        simpleScore = successorGameState.getScore() - currentGameState.getScore()
        ghostScore, foodScore = 0, 0
        ghostWeight, foodWeight, scoreWeight = 2, 1, 3
        if newGhostStates:
            distances = [util.manhattanDistance(ghost.getPosition(), newPos) for ghost in newGhostStates]
            dist = min(distances)
            if dist == 0:
                ghostScore = -100
            else:
                ghostScore = -0.5 / dist
        if newFood:
            distances = [util.manhattanDistance(food, newPos) for food in newFood]
            foodScore = 0.5 / min(distances)
        finalScore = ghostWeight * ghostScore + foodWeight * foodScore + scoreWeight * simpleScore
        return finalScore


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game

          gameState.isWin():
            Returns whether or not the game state is a winning state

          gameState.isLose():
            Returns whether or not the game state is a losing state
        """
        ghostsNum = gameState.getNumAgents() - 1
         # 1 if it is the pacmans turn


        def ghostAction(state, num, depth):

            if state.isLose() or state.isWin():
                return self.evaluationFunction(state)
            actions = state.getLegalActions(num)
            successorStates = [state.generateSuccessor(num, action) for action in actions]
            if num < ghostsNum:
                return min([ghostAction(successor, num + 1, depth) for successor in successorStates])
            elif depth == self.depth:
                return min([self.evaluationFunction(successor) for successor in successorStates])
            else:
                return min([pacmanAction(successor, depth + 1) for successor in successorStates])

        def pacmanAction(state, depth):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            actions = state.getLegalActions(0)
            successorStates = [state.generateSuccessor(0, action) for action in actions]
            utilities = [ghostAction(state, 1, depth) for state in successorStates]
            if utilities:
                maxUtil = max(utilities)
            else:
                maxUtil = None
            if depth != 1:
                return maxUtil
            maxUtilIndices = [i for i in range(len(utilities)) if utilities[i] == maxUtil]
            return actions[random.choice(maxUtilIndices)]

        return pacmanAction(gameState, 1)


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        ghostsNum = gameState.getNumAgents() - 1

        def pacmanAction(state, depth, a, b):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            actions = state.getLegalActions(0)
            v = float('-inf')
            lastAction = None
            for action in actions:
                successor = state.generateSuccessor(0, action)
                utility = ghostAction(successor, 1, depth, a, b)
                if utility > v:
                    v = utility
                    lastAction = action
                if v > b: break
                a = max(a, v)
            if depth != 1:
                return v
            return lastAction

        def ghostAction(state, num, depth, a, b):
            if state.isLose() or state.isWin():
                return self.evaluationFunction(state)
            v = float("inf")
            moves = state.getLegalActions(num)

            # iterarting the through the ghosts
            if num < ghostsNum:
                for move in moves:
                    nextState = state.generateSuccessor(num, move)
                    comp = ghostAction(nextState, num + 1, depth, a, b)
                    v = min(comp, v)
                    if v < a:
                        return v
                    elif v < b:
                        b = v
                return v

            # Reach the depth
            if depth == self.depth:
                for move in moves:
                    nextState = state.generateSuccessor(num, move)
                    comp = self.evaluationFunction(nextState)
                    v = min(comp, v)
                    if v < a:
                        return v
                    elif v < b:
                        b = v
                return v

            # going down another depth
            for move in moves:
                nextState = state.generateSuccessor(num, move)
                comp = pacmanAction(nextState, depth + 1, a, b)
                v = min(comp, v)
                if v < a:
                    return v
                elif v < b:
                    b = v
            return v

        return pacmanAction(gameState, 1, float('-inf'), float('inf'))



class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        ghostsNum = gameState.getNumAgents() - 1
         # 1 if it is the pacmans turn

        def average(l):
            return sum(l)/len(l)


        def ghostAction(state, num, depth):

            if state.isLose() or state.isWin():
                return self.evaluationFunction(state)
            actions = state.getLegalActions(num)
            successorStates = [state.generateSuccessor(num, action) for action in actions]
            if num < ghostsNum:
                return average([ghostAction(successor, num + 1, depth) for successor in successorStates])
            elif depth == self.depth:
                return average([self.evaluationFunction(successor) for successor in successorStates])
            else:
                return average([pacmanAction(successor, depth + 1) for successor in successorStates])

        def pacmanAction(state, depth):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            actions = state.getLegalActions(0)
            successorStates = [state.generateSuccessor(0, action) for action in actions]
            utilities = [ghostAction(state, 1, depth) for state in successorStates]
            if utilities:
                maxUtil = max(utilities)
            else:
                maxUtil = None
            if depth != 1:
                return maxUtil
            maxUtilIndices = [i for i in range(len(utilities)) if utilities[i] == maxUtil]
            return actions[random.choice(maxUtilIndices)]

        return pacmanAction(gameState, 1)

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: Essentially, we identified the different methods of determing a 'value' for a state: we decided
      that promixity to the nearest ghost, food element, the score of the state itself, and whether or not ghosts were
      scared to be good metrics. As you can see in the weights section, we ordered them in terms of what we thought
      their priority should be, and used those as weights in a summation later on. We determined points for food
      and ghost proximity using manhattan distances, and used a reciprocal to create behavior such that the score
      would lower if you were closer to a ghost, or get larger if you were close to food, and vice versa for moving
      away from these elements. Being on a shared state with a ghost was an extremely undesirable score so we
      made that -infinity. Essentially, avoid dying. Inversely, getting the ghosts in a scared state was desirable so
      we added a large number of points for that. We played with the weights a lot to determine a good strategy, and
      this ordering produced an average score of 1157 so we were satisfied.
      
    """

    ghosts = currentGameState.getGhostStates()
    food = currentGameState.getFood().asList()
    timers = [ghost.scaredTimer for ghost in ghosts]
    position = currentGameState.getPacmanPosition()
    foodScore, ghostScore, timerScore = 0, 0, 0
    timerWeight, foodWeight, ghostWeight, scoreWeight = 1, 2, 3, 4

    if food:
        distances = [util.manhattanDistance(food, position) for food in food]
        foodScore = 0.5 / min(distances)
    if ghosts:
        distances = [util.manhattanDistance(ghost.getPosition(), position) for ghost in ghosts]
        dist = min(distances)
        if dist == 0:
            ghostScore = -100
        else:
            ghostScore = -0.5 / dist
    for time in timers:
        if time:
            timerScore = 100
            break;
    return foodScore * foodWeight + ghostScore * ghostWeight + currentGameState.getScore() * scoreWeight + timerScore


# Abbreviation
better = betterEvaluationFunction

