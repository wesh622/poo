package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class ArticleTest {

	@Test
	public void testGetContent() {
		diary.Article m = new diary.Article(1259838000, "Jean-Luc Picard", "Space the final frontier");
		String expectedS = "Space the final frontier";
		String valueS = m.getContent();
		assertEquals(expectedS, valueS);
	
		diary.Article m2 = new diary.Article(1259838000, "Quark", "Ferengi rules");
		expectedS = "Ferengi rules";
		valueS = m2.getContent();
		assertEquals(expectedS, valueS);		
	}

}
