package diary;

public class Video extends AbstractMedia{
    String url;
    String title;
    int length;

    public Video(long date,String author,String url, String title, int length){
        super(date, author);
        this.url = url;
        this.title = title;
        this.length = length;
    }

    public String getURL(){
        return this.url;
    }

    public String getTitle(){
        return this.title;
    }

    public int getLength(){
        return this.length;
    }
}
