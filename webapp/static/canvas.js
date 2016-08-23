function select_all_fn() {
    stmts = document.getElementById("indra_stmts");
    for (var i=0; i < stmts.options.length; i++) {
      stmts.options[i].selected = true;
      }
    };

function select_none_fn() {
    stmts = document.getElementById("indra_stmts");
    for (var i=0; i < stmts.options.length; i++) {
      stmts.options[i].selected = false;
      }
    };
