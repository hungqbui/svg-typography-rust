use std::fs;
use std::io::Result;
use usvg::{NodeExt, NodeKind, Options, Tree, TreeParsing, TreeWriting, XmlOptions};
use std::collections::{HashMap, HashSet};
use std::hash::{Hash, Hasher};

fn get_hash(t : &Vec<f64>) -> u64 {
    let mut s = std::collections::hash_map::DefaultHasher::new();
    for &i in t {
        i.to_bits().hash(&mut s);
    }
    s.finish()
}

fn get_bbox(root : &usvg::Node, counter: &mut u32, smap: &mut HashMap<String, Vec<f64>>, vset: &mut HashSet<u64>) {
    // let mut level_bound = Vec::<usvg::PathBbox>::new();
    for child in root.descendants() {
        *counter += 1;
        let cur_id = &format!("object_{}", counter);
        if let NodeKind::Group(ref mut g) = *child.borrow_mut() {
            g.id = cur_id.to_string();
        }
        if let Some(b)= child.calculate_bbox() {
            // level_bound.push(b);
            // id_list.push(cur_id.to_string());
            let v = vec![b.left(), b.right(), b.top(), b.bottom()];
            let hash = get_hash(&v);
            if vset.contains(&hash) {
                continue;
            }
            vset.insert(hash);
            smap.insert(cur_id.to_string(), v);
        }
    }
    // total.extend(level_bound);
}


fn main() -> Result<()> {
    let opt = Options::default();
    
    for entry in fs::read_dir("./svgs")? {
        let entry : fs::DirEntry = entry?;
        let path = entry.path();
        

        if path.is_file() && path.extension().and_then(|s| s.to_str()) == Some("svg") {
            let svg_string = fs::read(&path)?;
            let file_name = path.file_name().unwrap().to_str().unwrap();

            let tree = Tree::from_data(&svg_string, &opt);

            // let mut all_bboxes = Vec::<PathBbox>::new();
            // let mut ids = Vec::<String>::new();

            let mut smap = HashMap::<String, Vec<f64>>::new();
            let mut vset = HashSet::<u64>::new();

            match tree {
                Ok(tree) => {

                    let size = tree.size;
                    let mut pm = resvg::tiny_skia::Pixmap::new(size.width() as u32, size.height() as u32).unwrap();
                    let mut id: u32 = 0;
                    

                    let restree = resvg::Tree::from_usvg(&tree);
                    restree.render(resvg::tiny_skia::Transform::default(), &mut pm.as_mut());
                    
                    pm.save_png("./pngs/".to_string() + file_name + ".png").unwrap();

                    // get_bbox(&tree.root, &mut all_bboxes, &mut id, &mut ids);
                    get_bbox(&tree.root, &mut id, &mut smap, &mut vset);

                    // let bounds = all_bboxes.clone().iter().map(|bbox| {
                    //     vec![bbox.left(), bbox.right(), bbox.top(), bbox.bottom()]
                    // }).collect::<Vec<Vec<f64>>>();

                    // let json = SerializeJson {
                    //     ids: ids,
                    //     bounds: bounds
                    // };
                    
                    let wopt = XmlOptions::default();
                    let new_svg = tree.to_string(&wopt);

                    let image_file = std::fs::File::create(format!("./jsons/{}.json", file_name))?;

                    fs::write(format!("./id_svg/{}_withID.svg", file_name), new_svg)?;
                    serde_json::to_writer_pretty(image_file, &smap)?;
                }
                Err(e) => {
                    panic!("Can't parse {}", e);
                }
            };

        }

    }

    Ok(())
}
