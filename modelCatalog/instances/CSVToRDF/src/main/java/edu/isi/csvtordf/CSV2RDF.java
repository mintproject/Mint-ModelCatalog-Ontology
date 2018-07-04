package edu.isi.csvtordf;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
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
    
    public static void main(String[] args){
        CSV2RDF test = new CSV2RDF();
        test.processFile("C:\\Users\\dgarijo\\Desktop\\ModelCatalogPopulation\\Model.csv");
        test.processFile("C:\\Users\\dgarijo\\Desktop\\ModelCatalogPopulation\\ModelConfiguration.csv");
        test.processFile("C:\\Users\\dgarijo\\Desktop\\ModelCatalogPopulation\\DatasetSpecification.csv");
        test.processFile("C:\\Users\\dgarijo\\Desktop\\ModelCatalogPopulation\\VariablePresentation.csv");
        test.instances.write(System.out,"JSON-LD");
//        test.instances.write(System.out,"TTL");
    }
    
}
