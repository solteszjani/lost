class Listing {
  final int id;
  final String kind;
  final String title;
  final String description;
  final String category;
  final String location;
  final String date;
  final String contact;
  final String? imageUrl;
  final String status;

  const Listing({
    required this.id, required this.kind, required this.title,
    required this.description, required this.category, required this.location,
    required this.date, required this.contact, this.imageUrl, required this.status,
  });

  factory Listing.fromJson(Map<String, dynamic> j) => Listing(
    id: j['id'] as int,
    kind: j['kind'] as String,
    title: j['title'] as String,
    description: j['description'] as String,
    category: j['category'] as String,
    location: j['location'] as String,
    date: j['date'] as String,
    contact: j['contact'] as String,
    imageUrl: j['image_url'] as String?,
    status: j['status'] as String? ?? 'active',
  );
}
