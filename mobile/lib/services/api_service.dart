import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/listing.dart';

class ApiService {
  // Android emulátor: 10.0.2.2; iOS szimulátor: 127.0.0.1.
  static const String baseUrl = String.fromEnvironment('API_URL', defaultValue: 'http://10.0.2.2:8000');

  static Future<List<Listing>> getListings({String? kind, String? category, String? query}) async {
    final uri = Uri.parse('$baseUrl/listings').replace(queryParameters: {
      if (kind != null && kind != 'Mindegyik') 'kind': kind,
      if (category != null && category != 'Összes kategória') 'category': category,
      if (query != null && query.trim().isNotEmpty) 'q': query.trim(),
    });
    final response = await http.get(uri).timeout(const Duration(seconds: 15));
    if (response.statusCode != 200) throw Exception('A bejelentések nem tölthetők be.');
    final data = jsonDecode(response.body) as List;
    return data.map((e) => Listing.fromJson(e as Map<String, dynamic>)).toList();
  }

  static Future<Listing> createListing(Map<String, String> fields, {String? imagePath}) async {
    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/listings'));
    request.fields.addAll(fields);
    if (imagePath != null) request.files.add(await http.MultipartFile.fromPath('image', imagePath));
    final streamed = await request.send().timeout(const Duration(seconds: 30));
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode != 201) {
      throw Exception('A bejelentés mentése nem sikerült: ${response.body}');
    }
    return Listing.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  static Future<void> reportListing(int id, String reason) async {
    final response = await http.post(
      Uri.parse('$baseUrl/listings/$id/report'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'reason': reason}),
    );
    if (response.statusCode != 201) throw Exception('A jelentés nem sikerült.');
  }
}
