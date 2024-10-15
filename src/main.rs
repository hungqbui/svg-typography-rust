use std::fs;
use std::io::Result;
use usvg::{ Options, Rect, Tree};

fn get_bbox(root : &usvg::Group, total : &mut Vec<Rect>) -> &Vec<Rect> {
    
    if !root.has_children() {
        return &vec![root.bounding_box()];
    }
    
    let mut level_bound = Vec::<Rect>::new();
    for node in root.children() {
        if let usvg::Node::Group(ref g) = node {
            let cur = get_bbox(g, total);
            level_bound.extend(cur);
        } else {
            level_bound.push(node.bounding_box());
        }
    }
    total.extend(level_bound);
    return &level_bound;
}

fn main() -> Result<()> {
    let opt = Options::default();
    
    for entry in fs::read_dir("./svgs")? {
        let entry : fs::DirEntry = entry?;
        let path = entry.path();
        
        if path.is_file() && path.extension().and_then(|s| s.to_str()) == Some("svg") {
            let svg_string = fs::read_to_string(path)?;

            let tree = Tree::from_str(&svg_string, &opt);

            match tree {
                Ok(tree) => {
                    for node in tree.root().children() {
                        println!("{:?}", node.bounding_box());
                    }
                },
                Err(e) => {
                    panic!("Can't parse {}", e);
                }
            };

        }

    }


    println!("Hello, world!");
    Ok(())
}
