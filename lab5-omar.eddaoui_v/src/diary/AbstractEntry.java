package diary;

public class AbstractEntry implements Attributable,Timestampable {
    private long date;
    private String author;

    public AbstractEntry(long date,String author){
        this.date = date;
        this.author = author;
    }

    public String getAuthor(){
        return this.author;
    }

    public long getTimestamp(){
        return this.date;
    }
}
