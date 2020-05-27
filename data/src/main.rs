extern crate rusqlite;

use rusqlite::{params, Connection, Result};
use rusqlite::NO_PARAMS;
use tempfile::NamedTempFile;

use std::io::BufReader;
use std::io::BufRead;
use std::fs::File;


#[derive(Debug)]
struct Rec {
    tok: String,
}

fn main() -> Result<()> {
    let tmpfile = NamedTempFile::new().unwrap();
    let conn = Connection::open(tmpfile.path())?;
    conn.execute(
        "CREATE TABLE data(
        tok varchar(255) UNIQUE,
        cnt int)",
        NO_PARAMS,
    )?;
    let mut insert_sql = conn.prepare("INSERT INTO data (tok, cnt) 
                VALUES (?1, 1) ON CONFLICT(tok) 
                DO UPDATE SET cnt = cnt + 1;")?;
    let file = BufReader::new(File::open("cs.tok").expect("Cannot open file.txt"));
    conn.execute("BEGIN TRANSACTION", NO_PARAMS)?;
    for line in file.lines() {
        for tok in line.unwrap().split_whitespace(){
            if tok.chars().next().unwrap().is_alphabetic() {
                insert_sql.execute(params![tok.to_lowercase()])?;
            }
        }
    }
    conn.execute("COMMIT TRANSACTION", NO_PARAMS)?;
    let mut stmt = conn.prepare("SELECT tok from data ORDER BY cnt DESC LIMIT 10000")?;
    let tok_iter = stmt.query_map(NO_PARAMS, |row| {
        Ok(Rec{
            tok: row.get(0)?
        })
    })?;

    for rec in tok_iter {
        println!("{}", rec.unwrap().tok);
    }
    Ok(())
}
