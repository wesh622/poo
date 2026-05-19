package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethod;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethodWithReturnType;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredConstructor;

import static org.junit.jupiter.api.ReflectionAssertions.assertInstanceOf;

public class ArticleDefTest {
	
	@Test
	public void testGetContent() {
		assertDeclaredMethod("diary.Article", "getContent", new String[] { }, "missing method getContent() in class Article");
		assertDeclaredMethodWithReturnType("diary.Article", "getContent", new String[] { }, "java.lang.String", "missing method getContent() in class Article");
	}

	public void testDeclaredConstructors() {		
		assertDeclaredConstructor("diary.Article", new String[] { "long", "java.lang.String", "java.lang.String" }, "missing constructor Article(long, String, String) in class Article");
	}
	
	@Test
	public void testSuperTypes() {
		diary.Article m = new diary.Article(1259838000, "Jean-Luc Picard", "Space the final frontier");
		assertInstanceOf(m, "diary.AbstractEntry");
		assertInstanceOf(m, "diary.Timestampable");
		assertInstanceOf(m, "diary.Attributable");
	}

}
