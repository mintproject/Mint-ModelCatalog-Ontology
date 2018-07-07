package edu.isi.csvtordf;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.OutputStream;
import org.apache.jena.ontology.Individual;
import org.apache.jena.ontology.OntClass;
import org.apache.jena.ontology.OntModel;
import org.apache.jena.ontology.OntProperty;
import org.apache.jena.ontology.OntResource;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Property;

/**
 * @author dgarijo
 */
public class CSV2RDF {
    OntModel instances;
    OntModel mcOntology;
    String instance_URI = "https://w3id.org/mint/instance#";
    
    public CSV2RDF(){
        instances = ModelFactory.createOntologyModel();   
        mcOntology = ModelFactory.createOntologyModel();
        mcOntology.read("https://w3id.org/mint/modelCatalog");
        mcOntology.read("https://w3id.org/mint/commons");//for some reason it's not loading imported ontologies.
//        mcOntology.write(System.out);
        System.out.println("MINT model catalog ontology loaded");
    }
    
    private void processFile(String path){
        String line = "";
        String cvsSplitBy = ",";
        String[] colHeaders = null;
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            while ((line = br.readLine()) != null) {
                String[] values = line.split(cvsSplitBy);
                if (colHeaders == null){
                    colHeaders = values;//first line
                }else{
                    //add individual (col 0)
                    Individual ind = instances.createClass(colHeaders[0]).createIndividual(instance_URI+values[0]);
                    for(int i =1; i<values.length;i++){
                        String rowValue = values[i].trim();
                        if(!rowValue.equals("")){
                            String property = colHeaders[i];
                            OntProperty p = mcOntology.getOntProperty(property);
                            OntClass range = p.getRange().asClass();
                            if(p.isDatatypeProperty()|| p.isAnnotationProperty()//to include rdfs label too
                                    ||p.toString().contains("usesUnit")||p.toString().contains("StandardVariable")){//HACK, THESE WILL BE PROPERTIES IN THE FUTURE.
                                //System.out.print(rowValue+" ");
                                ind.addProperty(p, rowValue);
                            }else{
                                //this works under the assumption that there is range class for a property.
                                if(rowValue.contains(";")){//multiple values
                                    String[] valuesAux = rowValue.split(";");
                                    for(String a:valuesAux){
                                        if(!a.equals("")){
                                            ind.addProperty((Property) p, instances.createIndividual(instance_URI+a,range));
                                        }
                                    }
                                }else{
                                    ind.addProperty((Property) p, instances.createIndividual(instance_URI+rowValue,range));
                                }
                            }
                        }
                    }
                }
            }

        } catch (IOException e) {
            System.err.println("Error"+e.getMessage());
        }
    }
    
    /**
     * Function to export the stored model as an RDF file, using ttl syntax
     * @param outFile name and path of the outFile must be created.
     */
    public static void exportRDFFile(String outFile, OntModel model, String mode){
        OutputStream out;
        try {
            out = new FileOutputStream(outFile);
            model.write(out,mode);
            //model.write(out,"RDF/XML");
            out.close();
        } catch (Exception ex) {
            System.out.println("Error while writing the model to file "+ex.getMessage() + " oufile "+outFile);
        }
    }
    
    public static void main(String[] args){
        CSV2RDF test = new CSV2RDF();
        test.processFile("C:\\Users\\dgarijo\\Documents\\GitHub\\Mint-ModelCatalog-Ontology\\modelCatalog\\instances\\Model.csv");
        test.processFile("C:\\Users\\dgarijo\\Documents\\GitHub\\Mint-ModelCatalog-Ontology\\modelCatalog\\instances\\ModelConfiguration.csv");
        test.processFile("C:\\Users\\dgarijo\\Documents\\GitHub\\Mint-ModelCatalog-Ontology\\modelCatalog\\instances\\DatasetSpecification.csv");
        test.processFile("C:\\Users\\dgarijo\\Documents\\GitHub\\Mint-ModelCatalog-Ontology\\modelCatalog\\instances\\VariablePresentation.csv");
//        test.instances.write(System.out,"JSON-LD");
//        test.instances.write(System.out,"TTL");
        exportRDFFile("modelCatalog.ttl", test.instances, "TTL");
        exportRDFFile("modelCatalog.json", test.instances, "JSON-LD");
    }
    
}
