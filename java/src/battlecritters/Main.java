package battlecritters;

import py4j.GatewayServer;

/**
 * Class to start the battle-critter battle server. Accessible through py4j.
 */
public class Main {
	/**
	 * Starts the battle-critter battle server. Accessible through py4j.
	 */
	public static void main(String[] args) {
		GatewayServer server = new GatewayServer(new EntryPoint());
		server.start();
		System.out.println("Gateway Server started");
	}
}