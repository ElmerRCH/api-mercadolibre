

def get_model_product(produc_attributes) -> str:
    
    name_model = ""
     
    for k in produc_attributes:
        if k["id"] == "MODEL":
            name_model = k["value_name"]
            break

    return name_model