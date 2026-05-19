package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class PhotoTest {

	@Test
	public void testGetURL() {
		diary.Photo p = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/logo.png", "Captain Photo");
		String expectedS = "http://www.startrek.com/img/logo.png";
		String valueS = p.getURL();
		assertEquals(expectedS, valueS);
	
		diary.Photo p2 = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/banner.png", "Captain Photo2");
		expectedS = "http://www.startrek.com/img/banner.png";
		valueS = p2.getURL();
		assertEquals(expectedS, valueS);		
	}

	@Test
	public void testCaption() {
		diary.Photo p = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/logo.png", "Captain Photo");
		String expectedS = "Captain Photo";
		String valueS = p.getCaption();
		assertEquals(expectedS, valueS);
	
		diary.Photo p2 = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/banner.png", "Captain Photo2");
		expectedS = "Captain Photo2";
		valueS = p2.getCaption();
		assertEquals(expectedS, valueS);		
	}

}
