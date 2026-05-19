package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class VideoTest {

	@Test
	public void testGetURL() {
		diary.Video v = new diary.Video(1259838000, "Jean-Luc Picard", "http://www.startrek.com/vids/trailer.mpg", "Trailer", 180);
		String expectedS = "http://www.startrek.com/vids/trailer.mpg";
		String valueS = v.getURL();
		assertEquals(expectedS, valueS);
	
		diary.Video v2 = new diary.Video(1259838000, "Jean-Luc Picard", "http://www.startrek.com/vids/trailer-hq.mp4", "Trailer Next", 360);
		expectedS = "http://www.startrek.com/vids/trailer-hq.mp4";
		valueS = v2.getURL();
		assertEquals(expectedS, valueS);		
	}

	@Test
	public void testGetTitle() {
		diary.Video v = new diary.Video(1259838000, "Jean-Luc Picard", "http://www.startrek.com/vids/trailer.mpg", "Trailer", 180);
		String expectedS = "Trailer";
		String valueS = v.getTitle();
		assertEquals(expectedS, valueS);
	
		diary.Video v2 = new diary.Video(1259838000, "Jean-Luc Picard", "http://www.startrek.com/vids/trailer-hq.mp4", "Trailer Next", 360);
		expectedS = "Trailer Next";
		valueS = v2.getTitle();
		assertEquals(expectedS, valueS);		
	}

	@Test
	public void testGetLength() {
		diary.Video v = new diary.Video(1259838000, "Jean-Luc Picard", "http://www.startrek.com/vids/trailer.mpg", "Trailer", 180);
		int expectedS = 180;
		int valueS = v.getLength();
		assertEquals(expectedS, valueS);
	
		diary.Video v2 = new diary.Video(1259838000, "Jean-Luc Picard", "http://www.startrek.com/vids/trailer-hq.mp4", "Trailer Next", 360);
		expectedS = 360;
		valueS = v2.getLength();
		assertEquals(expectedS, valueS);		
	}


}
