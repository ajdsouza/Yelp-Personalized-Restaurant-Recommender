<?php 
    $db = new SQLite3('Data/datatouille.db');
    $results = $db->query('SELECT user_id,name FROM yelp_users LIMIT 10');
    while ($row = $results->fetchArray()) {
      echo "<option value=\"".$row["user_id"]."\">".$row["name"]."</option>\n";
    }
?>
