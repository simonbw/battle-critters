package battlecritters.critterloader;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

/**
 * Loads classes dynamically from their .class files. Only loads the first class dynamically. Following classes are
 * loaded with the fallback loader given.
 */
public class CritterClassLoader extends ClassLoader {

	/**
	 * The whitelist of name prefixes allowed for default loading. Allowing reflect might be unsafe, but it seemed to be needed for something.
	 */
	static final String[] ALLOWED_PACKAGES = { "java.lang", "battlecritters.battle", "sun.reflect" };

	/**
	 * The package that this
	 */
	String localPackage;

	public CritterClassLoader(String critterName) {
		super(CritterClassLoader.class.getClassLoader());
		localPackage = critterName.substring(0, critterName.lastIndexOf("."));
		System.out.println("new critter loader with local package: " + localPackage);
	}

	/**
	 * Load a class.
	 * @param  name full name of the class
	 * @return      the class
	 */
	public Class loadClass(String name) throws ClassNotFoundException {
		System.out.println("loading:" + name + " ...");

		// Access the critter and custom load
		if (name.startsWith(localPackage)) {
			System.out.println("using custom loading");
			try {
				byte[] data = loadClassData(name);
				return defineClass(name, data, 0, data.length);
			} catch (IOException e) {
				throw new ClassNotFoundException("class " + name + " not found: " + e.toString());
			}
		}
		// Use default loading on standard packages
		for (String allowedPackage : ALLOWED_PACKAGES) {
			if (name.startsWith(allowedPackage)) {
				System.out.println("using standard loading");
				return super.loadClass(name);
			}
		}
		// otherwise, not allowed
		System.out.println("could not load class: " + name);
		throw new ClassNotFoundException("class " + name + " is unavailable");
	}

	/**
	 * Return a byte array for a specific class name.
	 *
	 * @param   name    The class name
	 * @return  The class info as byte data
	 * @throws  IOException when file not found
	 */
	private byte[] loadClassData(String name) throws IOException {
		File f = getClassFile(name);
		byte buffer[] = new byte[(int) f.length()];
		DataInputStream dataStream = new DataInputStream(new FileInputStream(f));
		dataStream.readFully(buffer);
		dataStream.close();
		return buffer;
	}

	/**
	 * Returns a file for the given class name, assuming the class
	 * @param  name the class name
	 * @return      the file containing the class
	 */
	private File getClassFile(String name) {
		String path = "java" + File.separator + "bin" + File.separator + name.replace(".", File.separator) + ".class";
		return new File(path);
	}

}
