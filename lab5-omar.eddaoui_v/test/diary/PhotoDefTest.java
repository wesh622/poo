package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethod;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethodWithReturnType;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredConstructor;

import static org.junit.jupiter.api.ReflectionAssertions.assertInstanceOf;

public class PhotoDefTest {
	
	@Test
	public void testDeclaredMethods() {		
		assertDeclaredMethod("diary.Photo", "getURL", new String[] { }, "missing method getURL() in class Photo");
		assertDeclaredMethodWithReturnType("diary.Photo", "getURL", new String[] { }, "java.lang.String", "missing method getURL() in class Photo");
		assertDeclaredMethodWithReturnType("diary.Photo", "getCaption", new String[] { }, "java.lang.String", "missing method getCaption() in class Photo");
	}

	@Test
	public void testDeclaredConstructors() {		
		assertDeclaredConstructor("diary.Photo", new String[] { "long", "java.lang.String", "java.lang.String", "java.lang.String" }, "missing constructor Photo(long, String, String, String) in class Photo");
	}
	
	@Test
	public void testSuperTypes() {
		diary.Photo p = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/logo.png", "Captain Photo");
		assertInstanceOf(p, "diary.AbstractMedia");
		assertInstanceOf(p, "diary.Keywordable");
		assertInstanceOf(p, "diary.Attributable");
		assertInstanceOf(p, "diary.Timestampable");
	}


}
