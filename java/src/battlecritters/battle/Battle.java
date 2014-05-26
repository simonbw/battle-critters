package battlecritters.battle;

import java.awt.Point;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import battlecritters.battle.Critter.Direction;
import battlecritters.critterloader.CritterClassLoader;

/**
 * A battle between Critters. Must add critters
 */
public class Battle {
	/**
	 * Default height of the battle
	 */
	private static final int DEFAULT_HEIGHT = 100;
	/**
	 * Default width of the battle
	 */
	private static final int DEFAULT_WIDTH = 100;
	/**
	 * Action taken if the critter fails to provide one
	 */
	public static final Critter.Action DEFAULT_ACTION = Critter.Action.LEFT;

	/**
	 * The default length of a battle in frames.
	 */
	public static final int DEFAULT_MAX_FRAME = 2000;
	/**
	 * The current frame.
	 */
	private int frame;
	/**
	 * Length in frames of the battle.
	 */
	private int maxFrame;
	/**
	 * The critters in the battle.
	 */
	private List<Class<? extends Critter>> critters;
	/**
	 * Size of the grid.
	 */
	private int height;
	/**
	 * Size of the grid.
	 */
	private int width;
	/**
	 * Holds the location of the critters.
	 */
	private Critter[][] grid;
	/**
	 * Stores extra information about the critters.
	 */
	private Map<Critter, CritterData> info;
	/**
	 * Stores the integer to send the critter as.
	 */
	private Map<Class<? extends Critter>, Integer> critterCompression;
	/**
	 * Stores the name of the class as stored in the database.
	 */
	private Map<Class<? extends Critter>, String> critterNames;

	/**
	 * Create a new battle with the default length.
	 */
	public Battle() {
		this(DEFAULT_MAX_FRAME);
	}

	/**
	 * Create a new battle with custom length.
	 *
	 * @param maxFrame
	 *            length in frames of the battle.
	 */
	public Battle(int maxFrame) {
		this(maxFrame, DEFAULT_WIDTH, DEFAULT_HEIGHT);
	}

	/**
	 * Create a new battle with custom length and dimensions
	 *
	 * @param maxFrame
	 *            length in frames of the battle.
	 * @param width
	 *            number of cells wide
	 * @param height
	 *            number of cells high
	 */
	public Battle(int maxFrame, int width, int height) {
		this.maxFrame = maxFrame;
		this.width = width;
		this.height = height;
		frame = -1;
		critters = new ArrayList<Class<? extends Critter>>();
		grid = new Critter[width][height];
		info = new HashMap<Critter, Battle.CritterData>();
		critterCompression = new HashMap<Class<? extends Critter>, Integer>();
		critterNames = new HashMap<Class<? extends Critter>, String>();
	}

	/**
	 * Add a critter class to the battle.
	 *
	 * @param ownerName
	 * @param critterName
	 */
	public void addCritter(String ownerName, String critterName) {
		if (frame >= 0) {
			throw new IllegalStateException("Cannot add Critters once the battle has begun");
		}
		String className = "battlecritters.critters." + ownerName + "." + critterName;

		Class<? extends Critter> critter = null;
		try {
			CritterClassLoader loader = new CritterClassLoader(className);
			critter = loader.loadClass(className).asSubclass(Critter.class);
		} catch (ClassNotFoundException e) {
			System.out.println(e);
		}
		if (critter != null) {
			critterCompression.put(critter, critterCompression.size());
			critterNames.put(critter, ownerName + "." + critterName);
			critters.add(critter);
		}
	}

	/**
	 * Initialize the battle.
	 */
	public void start() {
		System.out.println("Battle Starting");
		frame = 0;

		int number = 30;

		Random r = new Random();
		for (Class<? extends Critter> C : critters) {
			Critter.Direction[] directions = Critter.Direction.values();
			for (int i = 0; i < number; i++) {
				Critter next;
				try {
					next = makeCritter(C);
				} catch (Exception e) {
					e.printStackTrace();
					return;
				}
				int x, y;
				do {
					x = r.nextInt(width);
					y = r.nextInt(height);
				} while (grid[x][y] != null);

				Critter.Direction d = directions[r.nextInt(directions.length)];
				grid[x][y] = next;

				info.put(next, new CritterData(new Point(x, y), d, 0));
			}
		}
	}

	/**
	 * Create a critter of the given class.
	 *
	 * @param critter
	 * @return
	 * @throws Exception
	 */
	private Critter makeCritter(Class<? extends Critter> critter) throws Exception {
		return critter.newInstance();
	}

	/**
	 * Return the move of a critter. If the critter errors or takes too long, returns the DEFAULT_MOVE.
	 * @param  c the critter
	 * @return   the move
	 */
	private Critter.Action getMove(Critter critter, CritterInfo info) {
		try {
			return critter.getMove(info);
		} catch (Exception e) {
			return DEFAULT_ACTION;
		}

		//////////////////////////////////////
		// Uncomment this stuff for timeout //
		//     Currently very slow          //
		//////////////////////////////////////

		// CritterMoveThread thread = new CritterMoveThread(critter, info);

		// thread.start();

		// long endTime = System.currentTimeMillis() + 100;
		// while (thread.isAlive()) {
		//  if (System.currentTimeMillis() > endTime) {
		//      System.out.println("Method Timed Out");
		//      break;
		//  }
		//  try {
		//      Thread.sleep(10);
		//  } catch (InterruptedException e) {
		//      // Do nothing
		//  }
		// }

		// return thread.move;
	}

	/**
	 * Advance to the next frame of the battle.
	 */
	public void nextFrame() {
		frame++;
		for (Critter critter : info.keySet().toArray(new Critter[0])) {
			CritterData data = info.get(critter);

			// happens when creature was infected earlier in this round
			if (data == null) {
				continue;
			}

			Point p = data.p;
			Point p2 = pointAt(p, data.direction);
			Critter.Action move = getMove(critter, getInfo(data, critter.getClass()));
			switch (move) {
			case LEFT:
				data.direction = rotate(rotate(rotate(data.direction)));
				break;
			case RIGHT:
				data.direction = rotate(data.direction);
				break;
			case HOP:
				if (inBounds(p2) && grid[p2.x][p2.y] == null) {
					grid[p2.x][p2.y] = grid[p.x][p.y];
					grid[p.x][p.y] = null;
					data.p = p2;
				}
				break;
			case INFECT:
				if (inBounds(p2) && grid[p2.x][p2.y] != null && grid[p2.x][p2.y].getClass() != critter.getClass()) {
					Critter other = grid[p2.x][p2.y];
					// remember the old critter's private data
					CritterData oldData = info.get(other);
					// then remove that old critter
					info.remove(other);
					// and add a new one to the grid
					try {
						grid[p2.x][p2.y] = makeCritter(critter.getClass());
					} catch (Exception e) {
						throw new RuntimeException("" + e);
					}
					// and add to the map
					info.put(grid[p2.x][p2.y], oldData);
					// and remember that we infected a critter
					data.infectCount++;
				}
				break;
			}
		}
	}

	/**
	 * @return true if the battle is over
	 */
	public boolean isOver() {
		return frame >= maxFrame;
	}

	/**
	 * Return the winner of the battle if the battle is over.
	 * @return {String} ownerName.critterName
	 */
	public String getWinner() {
		String winner = null;
		int winnerScore = -1;

		Map<String, Integer> scores = getScores();
		for (String critter : scores.keySet()) {
			if (scores.get(critter) >= winnerScore) {
				winnerScore = scores.get(critter);
				winner = critter;
			}
		}

		return critterNames.get(winner);
	}

	/**
	 * Return the scores
	 * @return [description]
	 */
	public Map<String, Integer> getScores() {
		Map<String, Integer> scores = new HashMap<String, Integer>();
		for (Class<? extends Critter> C : critters) {
			scores.put(critterNames.get(C), 0);
		}

		for (int x = 0; x < grid.length; x++) {
			for (int y = 0; y < grid[x].length; y++) {
				if (grid[x][y] != null) {
					String name = critterNames.get(grid[x][y].getClass());
					scores.put(name, scores.get(name) + 1);
				}
			}
		}

		return scores;
	}

	/**
	 * @return The current frame
	 */
	public int getFrame() {
		return frame;
	}

	/**
	 * Returns True if the position is on the grid.
	 *
	 * @param x
	 * @param y
	 * @return True if position is on the grid
	 */
	private boolean inBounds(int x, int y) {
		return (x >= 0 && x < width && y >= 0 && y < height);
	}

	/**
	 * Returns True if the position is on the grid.
	 *
	 * @param p
	 * @return True if position is on the grid
	 */
	private boolean inBounds(Point p) {
		return inBounds(p.x, p.y);
	}

	/**
	 * Returns the direction directly clockwise from d
	 *
	 * @param d
	 * @return
	 */
	private Critter.Direction rotate(Critter.Direction d) {
		switch (d) {
		case EAST:
			return Direction.SOUTH;
		case NORTH:
			return Direction.EAST;
		case SOUTH:
			return Direction.WEST;
		case WEST:
			return Direction.NORTH;
		default:
			return null;
		}
	}

	/**
	 * Returns the point one coordinate away from p in direction d.
	 *
	 * @param p
	 *            starting point
	 * @param d
	 *            direction
	 * @return result point
	 */
	private Point pointAt(Point p, Critter.Direction d) {
		switch (d) {
		case EAST:
			return new Point(p.x + 1, p.y);
		case NORTH:
			return new Point(p.x, p.y - 1);
		case SOUTH:
			return new Point(p.x, p.y + 1);
		case WEST:
			return new Point(p.x - 1, p.y);
		default:
			return null;
		}
	}

	/**
	 * Return the type of neighbor for a critter at a point.
	 *
	 * @param p
	 *            point
	 * @param original
	 *            class of the critter
	 * @return
	 */
	private Critter.Neighbor getStatus(Point p, Class<? extends Critter> original) {
		if (!inBounds(p))
			return Critter.Neighbor.WALL;
		else if (grid[p.x][p.y] == null)
			return Critter.Neighbor.EMPTY;
		else if (grid[p.x][p.y].getClass() == original)
			return Critter.Neighbor.SAME;
		else
			return Critter.Neighbor.OTHER;
	}

	/**
	 * Returns the info to pass to a given critter.
	 *
	 * @param data
	 * @param original
	 * @return
	 */
	private Info getInfo(CritterData data, Class<? extends Critter> original) {
		Critter.Neighbor[] neighbors = new Critter.Neighbor[4];
		Critter.Direction d = data.direction;
		for (int i = 0; i < 4; i++) {
			neighbors[i] = getStatus(pointAt(data.p, d), original);
			d = rotate(d);
		}
		return new Info(neighbors, data.direction, data.infectCount);
	}

	public String toString() {
		StringBuilder buffer = new StringBuilder();

		for (Critter critter : info.keySet().toArray(new Critter[0])) {
			CritterData data = info.get(critter);
			buffer.append(critterCompression.get(critter.getClass()) + " ");
			buffer.append(data.p.x + " ");
			buffer.append(data.p.y + " ");
			buffer.append(" ");
			buffer.append("\n");
		}

		return buffer.toString();
	}

	/**
	 * Stores extra data about a critter.
	 */
	private class CritterData {
		public Point p;
		public Critter.Direction direction;
		public int infectCount;

		public CritterData(Point p, Critter.Direction d, int infectCount) {
			this.p = p;
			this.direction = d;
			this.infectCount = infectCount;
		}

		public String toString() {
			return p + " " + direction + " " + infectCount;
		}
	}

	/**
	 * Info to pass to the critter for getMove.
	 */
	private static class Info implements CritterInfo {
		private Critter.Neighbor[] neighbors;
		private Critter.Direction direction;
		private int infectCount;

		public Info(Critter.Neighbor[] neighbors, Critter.Direction d, int infectCount) {
			this.neighbors = neighbors;
			this.direction = d;
			this.infectCount = infectCount;
		}

		public Critter.Neighbor getFront() {
			return neighbors[0];
		}

		public Critter.Neighbor getBack() {
			return neighbors[2];
		}

		public Critter.Neighbor getLeft() {
			return neighbors[3];
		}

		public Critter.Neighbor getRight() {
			return neighbors[1];
		}

		public Critter.Direction getDirection() {
			return direction;
		}

		public int getInfectCount() {
			return infectCount;
		}
	}
}
