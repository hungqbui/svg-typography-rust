use std::fs;
use std::io::Result;
use usvg::{Options, Rect, Tree};
use serde::{Serialize, Deserialize};

fn get_bbox(root : &usvg::Group, total : &mut Vec<Rect>) {
    
    if !root.has_children() {
        return;
    }
    
    let mut level_bound = Vec::<Rect>::new();
    for node in root.children() {
        if let usvg::Node::Group(ref g) = node {
            get_bbox(g, total);
        }
        level_bound.push(node.bounding_box());
    }
    total.extend(level_bound);
}

#[derive(Serialize, Deserialize, Debug)]
struct SerializeJson {
    bounds: Vec<Vec<f32>>
}

fn main() -> Result<()> {
    let opt = Options::default();
    
    for entry in fs::read_dir("./svgs")? {
        let entry : fs::DirEntry = entry?;
        let path = entry.path();
        

        if path.is_file() && path.extension().and_then(|s| s.to_str()) == Some("svg") {
            let svg_string = fs::read_to_string(&path)?;
            let file_name = path.file_name().unwrap().to_str().unwrap();

            let tree = Tree::from_str(&svg_string, &opt);

            let mut all_bboxes = Vec::<Rect>::new();

            match tree {
                Ok(tree) => {
                    get_bbox(&tree.root(), &mut all_bboxes);
                    for bbox in &all_bboxes {
                        println!("{} {} {} {}\n", bbox.x(), bbox.y(), bbox.width(), bbox.height());
                    }

                    let bounds = all_bboxes.clone().iter().map(|bbox| {
                        vec![bbox.left(), bbox.right(), bbox.top(), bbox.bottom()]
                    }).collect::<Vec<Vec<f32>>>();

                    let json = SerializeJson {
                        bounds: bounds
                    };

                    let file = std::fs::File::create(format!("./jsons/{}.json", file_name))?;
                    serde_json::to_writer_pretty(file, &json)?;
                }
                Err(e) => {
                    panic!("Can't parse {}", e);
                }
            };

        }

    }

    Ok(())
}
