package dev.tsl9.morphe;
import java.nio.file.*;
import java.util.*;
/** Replays receive metadata with synthetic bytes; never opens BLE or retains real payload. */
public final class LiveReplayTests {
    public static void main(String[] args)throws Exception{
        long[] now={0};LiveVehicleData model=new LiveVehicleData(()->now[0]);Set<Integer> ids=new HashSet<>();int rows=0;
        for(String line:Files.readAllLines(Paths.get(args[0]))){String[] p=line.split("\\t");now[0]=Long.parseLong(p[0]);int id=Integer.parseInt(p[1],16),length=Integer.parseInt(p[2]);byte[] frame=new byte[2+length];frame[0]=(byte)(id>>>8);frame[1]=(byte)id;if(!model.onCan(frame))throw new AssertionError("capture metadata rejected");ids.add(id);rows++;}
        if(model.canCount()!=rows||model.idCount()!=Math.min(ids.size(),256)||model.recent(50).size()!=Math.min(ids.size(),50))throw new AssertionError("capture aggregation mismatch");
        System.out.println("LiveReplayTests passed: "+rows+" receive-metadata rows / "+ids.size()+" IDs; synthetic bytes, no transmission or signal-meaning validation.");
    }
}
