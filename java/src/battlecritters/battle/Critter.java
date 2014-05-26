package battlecritters.battle;

// CSE 142 Homework 8 (Critters)
// Authors: Stuart Reges and Marty Stepp
//
// This is the superclass of all of the Critter classes. Your class should
// extend this class. The class provides several kinds of constants:
//
// type Neighbor : WALL, EMPTY, SAME, OTHER
// type Action : HOP, LEFT, RIGHT, INFECT
// type Direction : NORTH, SOUTH, EAST, WEST
//
// Override the following methods to change the behavior of your Critter:
//
// public Action getMove(CritterInfo info)
// public Color getColor()
// public String toString()
//
// The CritterInfo object passed to the getMove method has the following
// available methods:
//
// public Neighbor getFront(); returns neighbor in front of you
// public Neighbor getBack(); returns neighbor in back of you
// public Neighbor getLeft(); returns neighbor to your left
// public Neighbor getRight(); returns neighbor to your right
// public Direction getDirection(); returns direction you are facing
// public int getInfectCount(); returns your current infect count
// (# of Critters you have infected)

import java.awt.Color;

/**
 * The base class for all critters to extend.
 * 
 * @author Stuart Reges and Marty Stepp and Simon Baumgardt-Wellander
 */
public class Critter {
	public static enum Neighbor {
		WALL, EMPTY, SAME, OTHER
	};

	public static enum Action {
		HOP, LEFT, RIGHT, INFECT
	};

	public static enum Direction {
		NORTH, SOUTH, EAST, WEST
	};

	protected static Neighbor WALL = Neighbor.WALL;
	protected static Neighbor EMPTY = Neighbor.EMPTY;
	protected static Neighbor SAME = Neighbor.SAME;
	protected static Neighbor OTHER = Neighbor.OTHER;
	protected static Action HOP = Action.HOP;
	protected static Action LEFT = Action.LEFT;
	protected static Action RIGHT = Action.RIGHT;
	protected static Action INFECT = Action.INFECT;
	protected static Direction NORTH = Direction.NORTH;
	protected static Direction SOUTH = Direction.SOUTH;
	protected static Direction EAST = Direction.EAST;
	protected static Direction WEST = Direction.WEST;

	/**
	 * This method should be overridden. Default action is turning left.
	 * 
	 * @param info
	 * @return
	 */
	public Action getMove(CritterInfo info) {
		return Action.LEFT;
	}

	/**
	 * This method exists for legacy purposes.
	 * 
	 * @return color
	 */
	public Color getColor() {
		return Color.BLACK;
	}

	/**
	 * This method exists for legacy purposes.
	 */
	public String toString() {
		return "?";
	}

	/**
	 * This prevents critters from trying to redefine the definition of object equality, which is important for the
	 * simulator to work properly.
	 */
	public final boolean equals(Object other) {
		return this == other;
	}
}